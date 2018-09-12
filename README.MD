# Copyright Yixue Zhang jedzhang@bu.edu

TITLE:EC601 PROJ1

The project ONLY work with Python3.6 

Please ensure you have the following packages before running this project:
1.tqdm
2.Pillow
3.google-cloud-vision
4.tweepy

Please input your own twitter api and google platform json into the python script before running.

Please run with "python3 proj1.py"

The program work as follows:
First you should input a tweeter account that you are interested in and then input the number of picture you want to get from it. If the number you entered is too large, the program would warn you and exit. Then the program would search from the account that you entered eariler for pictures.
If the program cannot find required amount of pictures, it would warn you and exit. If the program find the required number of pictures, it would download them to a local folder with the name of the account. The program would resize all pictures in the folder to 1280*720 and then assemble to a mp4 file, with every picture for a second. If the there is another mp4 file with the same name, it would warn you and you should input "y" to continue. Finally, the program would call for google vision analysis for every image in the folder and generate a file called 'Label_detection.txt', it contains every file name with its detected features.

If the program fails or you have any question, feel free to contect me at jedzhang@bu.edu

