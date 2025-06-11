import cv2
import numpy as np
import os

ID_START_MARKER = 0
ID_END_MARKER = 1

def detect_markers(frame, use_advanced=False):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if use_advanced:
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.equalizeHist(gray_frame)
        gray_frame = cv2.GaussianBlur(gray_frame, (3, 3), 0)

        gray_thresh = cv2.adaptiveThreshold(gray_frame, 255, cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY, 11, 5)

    aruco_dict_type = cv2.aruco.DICT_APRILTAG_16H5
    aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict_type)
    aruco_parameters = cv2.aruco.DetectorParameters()

    if use_advanced:
        # Parametry detekcji
        aruco_parameters.adaptiveThreshConstant = 5
        aruco_parameters.adaptiveThreshWinSizeMin = 3
        aruco_parameters.adaptiveThreshWinSizeMax = 51
        aruco_parameters.adaptiveThreshWinSizeStep = 2
        aruco_parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX

        aruco_parameters.minMarkerPerimeterRate = 0.005
        aruco_parameters.maxMarkerPerimeterRate = 6.0
        aruco_parameters.minCornerDistanceRate = 0.005
        aruco_parameters.minDistanceToBorder = 0

    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_parameters)
    corners, ids, rejected = detector.detectMarkers(gray)

    return corners, ids, rejected

def draw_markers_and_save(frame, corners, ids, output_path):
    marker_centers = {}
    marker_corners_data = {}

    if ids is not None:
        for i, marker_id in enumerate(ids):
            current_id = marker_id[0]
            marker_corners = corners[i].reshape((4, 2)).astype(int)
            center = tuple(np.mean(marker_corners, axis=0).astype(int))
            marker_centers[current_id] = center
            marker_corners_data[current_id] = marker_corners

        #Strzałka
        if ID_START_MARKER in marker_centers and ID_END_MARKER in marker_centers:
            cv2.arrowedLine(frame, marker_centers[ID_START_MARKER], marker_centers[ID_END_MARKER],
                            (255, 0, 0), 5, tipLength=0.5)

        #Kontury
        for current_id, corners in marker_corners_data.items():
            cv2.polylines(frame, [corners.reshape((-1, 1, 2))], True, (0, 255, 0), 5)
            cv2.putText(frame, f"ID: {current_id}", marker_centers[current_id],
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.imwrite(output_path, frame)
    print(f"Zapisano: {output_path}")

    return len(ids) if ids is not None else 0

def process_image_with_aruco(image_path, output_folder):
    frame = cv2.imread(image_path)
    corners, ids, _ = detect_markers(frame, use_advanced=False)


    found_ids = set(ids.flatten()) if ids is not None else set()
    if not ({ID_START_MARKER, ID_END_MARKER} <= found_ids):
        # Dokladniejsza detekcja
        corners, ids, _ = detect_markers(frame, use_advanced=True)

    output_image_path = os.path.join(output_folder, os.path.basename(image_path))
    return draw_markers_and_save(frame, corners, ids, output_image_path)

input_folder = '06_loop'
output_folder = '06_loop_id'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)
total_markers = 0

for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
        image_path = os.path.join(input_folder, filename)
        count = process_image_with_aruco(image_path, output_folder)
        total_markers += count

print(f"Wykryte znaczniki: {total_markers}")
