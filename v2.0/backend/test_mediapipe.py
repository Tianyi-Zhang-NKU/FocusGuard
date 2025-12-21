import mediapipe as mp
try:
    print("Initializing MediaPipe Pose...")
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    print("MediaPipe Pose initialized successfully.")
    pose.close()
except Exception as e:
    print(f"Error initializing MediaPipe Pose: {e}")

try:
    print("Initializing MediaPipe FaceMesh...")
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)
    print("MediaPipe FaceMesh initialized successfully.")
    face_mesh.close()
except Exception as e:
    print(f"Error initializing MediaPipe FaceMesh: {e}")
