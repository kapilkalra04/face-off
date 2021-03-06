# The pre-trained model was provided by https://github.com/iwantooxxoox/Keras-OpenFace #

import tensorflow as tf
import numpy as np
import cv2
import glob
import pre_processing2 as pre
import matplotlib.pyplot as plt


# loader function to load the tf model from a frozen graph
def load_graph(frozen_graph_filename):
    with tf.gfile.GFile(frozen_graph_filename, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    with tf.Graph().as_default() as graph:
        tf.import_graph_def(
            graph_def, 
            input_map=None, 
            return_elements=None, 
            producer_op_list=None
        )
        
    return graph


if __name__ == '__main__':
	# call the loader function
    graph = load_graph('src/20180402-114759/20180402-114759.pb')
    
    # 2D array to store the images' pixel values whose embeddings have to be created 
    faceList = []
    for imagePath in glob.glob('data/library/train2/*'):
        # loading cropped,RGBscale,aligned (160,160)sized faces as reqd by FaceNet
        faceList.append(np.expand_dims(cv2.resize(pre.getFaceColor(imagePath),(160,160)), axis=0))
        
    # start the tf session    
    with tf.Session(graph=graph) as sess:
        # map variables to the tf model's layers
        images_placeholder = graph.get_tensor_by_name("import/input:0")
        embeddings = graph.get_tensor_by_name("import/embeddings:0")
        phase_train_placeholder = graph.get_tensor_by_name("import/phase_train:0")
       
        # generate input data in the correct format
        faceListInput = np.concatenate(faceList, axis=0)
        # normalize the input pixel values
        faceListInput = np.float32(faceListInput)/255.0
        print faceListInput.shape

        # prepare data
        feedDict = {phase_train_placeholder: False, images_placeholder: faceListInput}
        
        # run to get image embeddings
        values = sess.run(embeddings,feedDict)

        # save embedding values 
        np.save('src/empEmbeddings',values)

       