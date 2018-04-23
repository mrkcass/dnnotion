set -xv
TF_INC="$(python -c 'import tensorflow as tf; print(tf.sysconfig.get_include())') -I/usr/local/lib/python2.7/dist-packages/tensorflow/include/external/nsync/public"
TF_LIB="$(python -c 'import tensorflow as tf; print(tf.sysconfig.get_lib())') -L/local/lib/python2.7/dist-packages/tensorflow/lib/external/nsync/public"
g++ -std=c++11 -shared word2vec_ops.cc word2vec_kernels.cc -o word2vec_ops.so -fPIC -I $TF_INC -L$TF_LIB -ltensorflow_framework -O2 -D_GLIBCXX_USE_CXX11_ABI=0