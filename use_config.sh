if [ -z "$1" ]
then
    echo "$0 creates a link named 'config' to a given configuration file"
    echo "Usage: ./$0 example.config"
    exit -1
fi

ln -sf $1 config
