from flask import Flask, render_template, request, send_file
import numpy as np
import os
import cv2 as cv
import random
import sys, string
#arcgisscripting

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/inputImages'

@app.route('/')
def main_page() -> 'html':
	return render_template('main.html', the_title='Welcome')

@app.route('/results', methods=['POST'])
def run_methods() -> 'html':
	run_number = random.randint(0,100000000)
	file1 = request.files['image-r']
	f = os.path.join(app.config['UPLOAD_FOLDER'], f"{run_number}-{file1.filename}")
	file2 = request.files['image-l']
	f2 = os.path.join(app.config['UPLOAD_FOLDER'], f"{run_number}-{file2.filename}")

	file1.save(f)
	file2.save(f2)

	# CONVERT BOTH IMAGES TO GRAYSCALE
	orig_img1 = cv.imread(f"static/inputImages/{run_number}-{file1.filename}")
	orig_gray1 = cv.cvtColor(orig_img1,cv.COLOR_BGR2GRAY)

	orig_img2 = cv.imread(f"static/inputImages/{run_number}-{file2.filename}")
	orig_gray2 = cv.cvtColor(orig_img2,cv.COLOR_BGR2GRAY)
	
	detectors = []
	descriptors = []
	num_of_keypoints = {}
	filenames = {}
	filename1 = f"{run_number}-{file1.filename}"
	filename2 = f"{run_number}-{file2.filename}"

	operation = request.form['operation']
	orientation = request.form['orientation']
	specified_keypoints = int(request.form['num-keypoints'])
	for key, value in request.form.items():
		if "detector" in key:
			detectors.append(value)

		if "descriptor" in key:
			descriptors.append(value)

	for detector in detectors:
		if detector == "Other-Detector":
			if operation == "matching":
				os.system("/Path/to/Other/Matching.exe enter variables after")
			else:
				os.system("/Path/to/Other/Stitching.exe enter variables after")
		else:
			if detector == "SURF-Detector":
				detector_object = cv.xfeatures2d.SURF_create(400) # Not able to specify how many keypoints, use response from detetected
			if detector == "SIFT-Detector":
				detector_object = cv.xfeatures2d.SIFT_create(specified_keypoints)
			if detector == "FAST-Detector":
				detector_object = cv.FastFeatureDetector_create() # Not able to specify how many keypoints, use response from detetected
			if detector == "ORB-Detector":
				detector_object = cv.ORB_create(specified_keypoints)
			if detector == "Harris-Detector":  # Not able to specify how many keypoints, use response from detetected
				harris_gray1 = np.float32(orig_gray1)
				harris_gray2 = np.float32(orig_gray2)
				dst1 = cv.cornerHarris(harris_gray1,2,3,0.04)
				dst2 = cv.cornerHarris(harris_gray2,2,3,0.04)
				
				detected_kp1 = np.argwhere(dst1 > 0.01 * dst1.max())
				detected_kp1 = [cv.KeyPoint(x[1], x[0], 1) for x in detected_kp1]
				
				detected_kp2 = np.argwhere(dst2 > 0.01 * dst2.max())
				detected_kp2 = [cv.KeyPoint(x[1], x[0], 1) for x in detected_kp2]


			# COMPUTE KEYPOINTS
			if not detector == "Harris-Detector":
				detected_kp1 = detector_object.detect(orig_gray1,None)
				detected_kp2 = detector_object.detect(orig_gray2,None)

			if ((detector == "SURF-Detector") or (detector == "SIFT-Detector") or (detector == "FAST-Detector") or (detector == "Harris-Detector")):
				if len(detected_kp1) > specified_keypoints:
					detected_kp1 = detected_kp1[:specified_keypoints]
				if len(detected_kp2) > specified_keypoints:
					detected_kp2 = detected_kp2[:specified_keypoints]
			
			kp1 = []
			kp2 = []
			# Check orientation
			if(orientation == 'downward'):
				for kp in detected_kp1:
					kp.angle = 90

				for kp in detected_kp2:
					kp.angle = 90

				for idx1, kp in enumerate(detected_kp1): 
					found = 1
					co_od_1 = list(kp.pt)

					for idx2, kp_compare in enumerate(detected_kp1):
						co_od_2 = list(kp_compare.pt)
						if idx2 <= idx1:
							continue
						else:
							size_test = abs(kp.size - kp_compare.size)
							response_test = abs(kp.response - kp_compare.response)

							if((co_od_1 == co_od_2) and (size_test <= 0.000000001) and (response_test <= 0.000000001)):
								found = 0
								break
					
					if found == 1:
						kp1.append(kp)


				for idx1, kp in enumerate(detected_kp2): 
					co_od_1 = list(kp.pt)
					found = 1
					for idx2, kp_compare in enumerate(detected_kp2):
						co_od_2 = list(kp_compare.pt)

						if idx2 <= idx1:
							continue
						else:
							size_test = abs(kp.size - kp_compare.size)
							response_test = abs(kp.response - kp_compare.response)
							if((co_od_1 == co_od_2) and (size_test <= 0.000000001) and (response_test <= 0.000000001)):
								found = 0
								break
					
					if found == 1:
						kp2.append(kp)

							
			else:
				for kp in detected_kp1:
					kp1.append(kp)

				for kp in detected_kp2:
					kp2.append(kp)

			for descriptor in descriptors:
				if descriptor == "SURF-Descriptor":
					descriptor_object = cv.xfeatures2d.SURF_create(400) # CURRENTLY RETIRED
				if descriptor == "SIFT-Descriptor":
					descriptor_object = cv.xfeatures2d.SIFT_create(specified_keypoints)
				if descriptor == "ORB-Descriptor":
					descriptor_object = cv.ORB_create() # CURRENTLY RETIRED
				if descriptor == "BRIEF-Descriptor":
					descriptor_object = cv.xfeatures2d.BriefDescriptorExtractor_create() # CURRENTLY RETIRED

				if operation == 'matching':

					new_kp1, des1 = descriptor_object.compute(orig_img1,kp1)
					new_kp2, des2 = descriptor_object.compute(orig_img2,kp2)

					num_of_keypoints[detector] = [len(kp1), len(kp2)]

					# create BFMatcher object
					bf = cv.BFMatcher(cv.NORM_L2,crossCheck=False)
					
					# Match descriptors.
					matches = bf.match(des1,des2)

					# Sort them in the order of their distance.
					matches = sorted(matches, key = lambda x:x.distance)

	# UNCOMMENT IF YOU WANT TO USE 1.5 *distance < all other distance measure and comment out the above line			
	#				for idx1, descriptor1 in enumerate(des1):
	#					for idx2, descriptor2 in enumerate(des2):
	#						dist_l2  = cv2.norm(descriptor1,descriptor2,cv2.NORM_L2) # Calculate distance between descriptors
	#						potential_match = bf.match(descriptor1,descriptor2) # Hold potential Match
	#
	#						distance = 1.5 * dist_l2 # Multiply distance by threshold (1.5)
	#						found = 1
	#
	#						for idx3, descriptor3 in enumerate(des2): # Iterate over each descritor
	#							if idx3 == idx2: # Skip previously calculated descriptor distance
	#								continue
	#							else:
	#								dist_other  = cv2.norm(descriptor1,descriptor3,cv2.NORM_L2) # Calculate new distance between other descriptor
	#								if distance > dist_other: # If previously calculate is larger, NOT a match
	#									found = 0
	#									break
	#
	#						if found == 1:
	#							matched_kp1.append(kp1[idx1])
	#							matched_kp2.append(kp2[idx2])
	#
	#							for match in potential_match:
	#								matches.append(match)

					# Draw Keypoints
					kp1_matched = []
					kp2_matched = []

					for i in range(20):
						kp1_matched.insert(i, new_kp1[matches[i].queryIdx])
						kp2_matched.insert(i, new_kp2[matches[i].trainIdx])


					img_kp_1 = cv.drawKeypoints(orig_img1,kp1_matched,None, flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
					img_kp_2 = cv.drawKeypoints(orig_img2,kp2_matched,None,flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
					# Draw first 20 matches.
					img3 = cv.drawMatches(img_kp_1,kp1,img_kp_2,kp2,matches[:20],None,flags=2)
					filenames[f"{detector}-{descriptor}"] = f"{run_number}-{operation}-{orientation}-{file1.filename}-{file2.filename}-{detector}-{descriptor}.png"
					new_filename = f"{run_number}-{operation}-{orientation}-{file1.filename}-{file2.filename}-{detector}-{descriptor}.png"
					cv.imwrite(f"static/savedImages/{new_filename}",img3)
				else:
					try:

						kp1, des1 = descriptor_object.compute(orig_img1,kp1)
						kp2, des2 = descriptor_object.compute(orig_img2,kp2)

						num_of_keypoints[detector] = [len(kp1), len(kp2)]

						bf = cv.BFMatcher()
						matches = bf.knnMatch(des1,des2, k=2)

						# Apply ratio test
						good = []
						for m in matches:
							if m[0].distance < 0.5*m[1].distance:
								good.append(m)

						matches = np.asarray(good)

						#if len(matches[:,0]) >= 4:
						src = np.float32([ kp1[m.queryIdx].pt for m in matches[:,0] ]).reshape(-1,1,2)
						dst = np.float32([ kp2[m.trainIdx].pt for m in matches[:,0] ]).reshape(-1,1,2)
						H, masked = cv.findHomography(src, dst, cv.RANSAC, 5.0)
						#print H
						#else:
						#	raise AssertionError("Can’t find enough keypoints.")

						dst = cv.warpPerspective(orig_img1,H,(orig_img2.shape[1] + orig_img1.shape[1], orig_img2.shape[0]))

						dst[0:orig_img2.shape[0], 0:orig_img2.shape[1]] = orig_img2
						filenames[f"{detector}-{descriptor}"] = f"{run_number}-{operation}-{orientation}-{file1.filename}-{file2.filename}-{detector}-{descriptor}.png"
						new_filename = f"{run_number}-{operation}-{orientation}-{file1.filename}-{file2.filename}-{detector}-{descriptor}.png"
						cv.imwrite(f"static/savedImages/{new_filename}",dst)
					except:
						filenames[f"{detector}-{descriptor}"] = f"ERROR{operation}-{orientation}-{file1.filename}-{file2.filename}-{detector}-{descriptor}.png"



	return render_template('results.html', 
							the_title='Results', 
							filename1 = f"{run_number}-{file1.filename}",
							filename2 = f"{run_number}-{file2.filename}",
							detectors_list = detectors,
							descriptors_list = descriptors,
							files_used = filenames,
							keypoints = num_of_keypoints,
							operation = operation,
							orientation = orientation,
							specific_num_keypoints = specified_keypoints)

@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
	path = f"static/savedImages/{filename}"
	return send_file(path, as_attachment=True)

app.run(debug=True)




# either check if detector has best reponse, if not, use top responses from keypoints
