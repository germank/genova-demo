#!/usr/bin/env python
#WARNING:
#requires ffmpeg and libSDL-1.2
import matplotlib
matplotlib.use('Agg')
from composes.semantic_space.space import Space
from composes.semantic_space.peripheral_space import PeripheralSpace
from composes.transformation.dim_reduction.svd import Svd
from composes.utils import io_utils
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import networkx as nx
import os.path
import glob
import logging
import argparse
plt.rcParams['savefig.bbox']='standard'
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

import errno, os
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

class AnimatedScatter(object):
    """An animated scatter plot using matplotlib.animations.FuncAnimation."""
    def __init__(self, center_word, years, spaces, stacked_space,
        scale_factor=10,
        transition_length=20):
        self.years = years
        self.center_word = center_word
        self.spaces = spaces
        self.stacked_space = stacked_space
        self.scale_factor = scale_factor
        self.transition_length=transition_length
        for year,sp in zip(years, spaces):
            if center_word not in sp.row2id:
                raise RuntimeError('{0} not found on year {1}'.format(
                center_word, year))
        self.vocab = list(set.union(*[set(sp.id2row) for sp in spaces])|
            {self.center_word})
        self.stream = self.data_stream()
        self.viewport = np.array([-0.2, 0.8, -0.2, 0.8])*self.scale_factor
        self.datalim = 0.9 * self.viewport

        self.not_in_space = np.array([50,50])
        # Setup the figure and axes...
        self.fig, self.ax = plt.subplots()
        # Then setup FuncAnimation.
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=20,
                                        frames=(len(spaces)-1)*self.transition_length-1,
                                           init_func=self.setup_plot)

    def setup_plot(self):
        """Initial drawing of the scatter plot."""
        year,(x, y,x_txt,y_txt) = next(self.stream)
        print 'USING YEAR', year
        self.year_text = self.ax.text((self.viewport[0]+self.viewport[1])/2, (self.viewport[2]+self.viewport[3])/2,year, horizontalalignment='center',
            fontsize=36)
        self.scat = self.ax.scatter(x, y)
        self.annotations = []
        for label,x_i,y_i,x_i_txt,y_i_txt in zip(self.vocab, x, y,x_txt, y_txt):
            an = plt.annotate(                                                                                                                                                                                                      
                label.decode('utf-8'),
                color = 'brown' if label == self.center_word else 'black',
                xy = (x_i, y_i), xytext = (x_i_txt, y_i_txt), size=13,
                textcoords = 'data', ha = 'left', va =
                'center',
                #bbox = dict(boxstyle = 'round,pad=0.5', fc = 'white',
                #alpha = 0.8),
                arrowprops = dict(arrowstyle = '->',
                connectionstyle = 'arc3,rad=0'))
            self.annotations.append(an)
        self.ax.axis(self.viewport)

        # For FuncAnimation's sake, we need to return the artist we'll be using
        # Note that it expects a sequence of artists, thus the trailing comma.
        return tuple([self.scat] + self.annotations)

    def data_stream(self):
        points = self.data_points()
        x0 = None
        y,x1 = next(points)
        for i,(y,x) in enumerate(points):
            x0 = x1
            x1 = x
            for a in np.arange(0,1,1.0/self.transition_length):
                yield y,(1-a) * x0 + a * x1

    def data_points(self):
        for i,(year,sp) in enumerate(zip(self.years,self.spaces)):
            coords = []
            logging.debug('Extracting data of space {0}'.format(i))
            center_coord = sp.get_row(self.center_word).mat
            self.present_words = []
            for j,w in enumerate(self.vocab):
                logging.debug('Obtaining word: {0}'.format(w))
                if w in sp.id2row:
                    coord = sp.get_row(w).mat - center_coord
                    logging.debug('Coordinates found: {0}'.format(
                        np.array(coord)[0]))
                    coords.append(np.array(coord)[0])
                    self.present_words.append(True)
                else:
                    logging.debug('Word not in space')
                    coords.append(self.not_in_space)
                    self.present_words.append(False)
            ret= np.array(coords)

            txt_pos = self.get_label_positions(ret)
            yield year,np.vstack((ret.transpose(),txt_pos.transpose()))

    def get_label_positions(self, ret, scale=1):
        center = np.mean(ret[np.array(self.present_words)], axis=0)
        txt_pos = np.zeros(ret.shape)
        left_bottom = np.array(self.datalim[0], self.datalim[2])
        right_top = np.array(self.datalim[1], self.datalim[3])
        for i,xy in enumerate(ret):
            txt_pos[i] = xy + (xy - center) * scale
            #clip to area
            txt_pos[i] = np.maximum(txt_pos[i], left_bottom)
            txt_pos[i] = np.minimum(txt_pos[i], right_top)

        return txt_pos

    def in_viewport(self, xy):
        left_bottom = np.array(self.viewport[0], self.viewport[2])
        right_top = np.array(self.viewport[1], self.viewport[3])
        return np.all(xy >= left_bottom) and np.all(xy <= right_top)
            
    def get_label_positions2(ret):
        G=nx.DiGraph()

        data_nodes = []
        init_pos = {}
        for j, b in enumerate(ret):
            x, y = b
            data_str = 'data_{0}'.format(j)
            txt_str = 'txt_{0}'.format(j)
            G.add_node(data_str)
            G.add_node(txt_str)
            #G[data_str]['pin'] = 'true'
            G.add_edge(txt_str, data_str, weight=10)
            data_nodes.append(data_str)
            init_pos[data_str] = (x, y)
            init_pos[txt_str] = (x, y)     

        pos = nx.spring_layout(G, pos=init_pos,
        iterations=2000,k=1,scale=10, weight=50)
        #pos = nx.graphviz_layout(G)
        
        txt_pos = np.zeros(ret.shape)
        for j in range(len(self.vocab)):
            txt_str = 'txt_{0}'.format(j)
            txt_pos[j] = np.array(pos[txt_str])
            
    def update(self, i):
        """Update the scatter plot."""
        print "Frame "+str(i)
        year,data = next(self.stream)

        self.scat.set_offsets(data[:2,:].transpose())
        x,y,x_txt,y_txt  = data
        self.year_text.s = year
        for i,(x_i,y_i,x_txt_i,y_txt_i) in enumerate(zip(x,y,x_txt,y_txt)):
            self.annotations[i].xy = (x_i,y_i)
            self.annotations[i].xytext = (x_txt_i,y_txt_i)
            
            

        # We need to return the updated artist for FuncAnimation to draw..
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.scat,

    def save(self, filename):
        w = animation.FFMpegWriter()
        self.ani.save(filename, writer=w, fps=30,  extra_args=['-vcodec', 'libx264'])

    def show(self):
        plt.show()



def add_year(sp, year):
    id2row = ["{0}_{1}".format(w,year) for w in sp.id2row]
    return Space(sp.cooccurrence_matrix, id2row, sp.id2column)


def vstack(s1, s2):
    if not s1:
        return  s2
    if not s2:
        return s1
    else:
        return Space.vstack(s1, s2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('space_dir')
    ap.add_argument('spaces_order')
    ap.add_argument('target_word')
    args = ap.parse_args()
    center_word = args.target_word #'cane'
    space_dir = args.space_dir
    space_filenames = [os.path.join(space_dir, os.path.basename(l.strip())) for l in file(args.spaces_order)]
    #'../03_extract_vectors/output/car'
    #space_filenames = glob.glob(os.path.join(space_dir, '*.pkl'))[:5]
    def figure_out_year(space_filename):
        try:
            basename = os.path.basename(space_filename)
            year = basename.split("_")
            if len(year) == 3:
                return "1" + year
            else:
                return year
        except:
            #We don't want to take any chances with this feature: if it doesn't
            #work, tough luck
            return ""
    years = map(figure_out_year, space_filenames)
    spaces = map(lambda f: io_utils.load(f), space_filenames)

    stacked = None
    for sp,space_filename in zip(spaces, space_filenames):
        stacked = vstack(stacked, add_year(sp,
        os.path.basename(space_filename)))

    stacked = stacked.apply(Svd(2))

    transformed_spaces = [PeripheralSpace(stacked, sp.cooccurrence_matrix,
    sp.id2row, sp.row2id) for sp in spaces]

    anim = AnimatedScatter(center_word,years, transformed_spaces, stacked,
    scale_factor=40)
    mkdir_p('output')
    anim.save('output/{0}.mp4'.format(center_word))
    




    

if __name__ == '__main__':
    main()
