#!/usr/bin/env python
# coding: utf-8
# Credits: https://github.com/wmazin/Visualizing-Quantum-Computing-using-fractals

# |
# | Library imports
# └───────────────────────────────────────────────────────────────────────────────────────────────────────
# Importing standard python libraries
from pathlib import Path
from typing import List
import traceback
import timeit

# Import additional python libraries
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

from selenium.common.exceptions import WebDriverException, NoSuchWindowException
from selenium.webdriver.common.by import By
from celluloid import Camera
from numpy import complex_

# Importing standard Qiskit libraries
from qiskit import QuantumCircuit
from qiskit.visualization import *  # plot_bloch_multivector

# self-coded libraries
from fractal_webclient import WebClient
from quantum_fractals_guidebook.utils.fractal_julia_calculations import set_1cn, set_2cn1, set_2cn2
from quantum_fractals_guidebook.utils.fractal_quantum_circuit import FractalQuantumCircuit

# |
# | Global settings for the script
# └───────────────────────────────────────────────────────────────────────────────────────────────────────
# Julia set calculation values
julia_iterations: int = 100
julia_escape_val: int = 2

# Image generation and animation values
GIF_ms_intervals: int = 200  # 200ms = 5 fps
number_of_frames: int = 60  # Total number of frames to generate

# Coordinate values in the Julia Set fractal image/frame
frame_resolution: int = 200  # Height and width
height: int = frame_resolution
width: int = frame_resolution
zoom: float = 1.0

x_start: float = 0
x_width: float = 1.5
x_min: float = x_start - x_width / zoom
x_max: float = x_start + x_width / zoom

y_start: float = 0
y_width: float = 1.5
y_min: float = y_start - y_width / zoom
y_max: float = y_start + y_width / zoom

# Create the basis 2D array for the fractal
x_arr = np.linspace(start=x_min, stop=x_max, num=width).reshape((1, width))
y_arr = np.linspace(start=y_min, stop=y_max, num=height).reshape((height, 1))
z_arr = (x_arr + 1j * y_arr)

# Create array to keep track in which iteration the points have diverged
div_arr = np.full(z_arr.shape, julia_iterations - 1, dtype='int64')

# Create Array to keep track on which points have not converged
con_arr = np.full(z_arr.shape, True, dtype=np.bool_)

# Dictionary to keep track of time pr. loop
timer = {"QuantumCircuit": 0.0, "Julia_calculations": 0.0, "Animation": 0.0, "Image": 0.0}

# |
# | Pathing, default folder and generated files, webclient
# └───────────────────────────────────────────────────────────────────────────────────────────────────────
# Set default path values
temp_image_folder = Path(Path.cwd(), "../img")
browser_file_path = f"file://{temp_image_folder}"
default_image_url = f"{browser_file_path}/2cn2.png"

# Start the Chromedriver and redirect to default image before removal
driver = WebClient(default_image_url=default_image_url).get_driver()  # ChromeDriver

# Remove previously generated files
if temp_image_folder.exists():
    for image in temp_image_folder.glob("*.*"):
        Path(image).unlink()
else:
    temp_image_folder.mkdir(parents=True, exist_ok=True)


# |
# | Defining the animation class to generate the images for the Quantum Fractal
# └───────────────────────────────────────────────────────────────────────────────────────────────────────
# Set default path values
temp_image_folder = Path(Path.cwd(), "../img")
browser_file_path = f"file://{temp_image_folder}"
default_image_url = f"{browser_file_path}/2cn2.png"

# Start the Chromedriver and redirect to default image before removal
driver = WebClient(default_image_url=default_image_url).get_driver()  # ChromeDriver

# Remove previously generated files
if temp_image_folder.exists():
    for image in temp_image_folder.glob("*.*"):
        Path(image).unlink()
else:
    temp_image_folder.mkdir(parents=True, exist_ok=True)


# |
# | Defining the animation class to generate the images for the Quantum Fractal
# └───────────────────────────────────────────────────────────────────────────────────────────────────────
class QuantumFractalImages:
    def __init__(self, sv_custom: complex_, sv_list: List[complex_], circ: QuantumCircuit):
        # Firstly, calculate the three types of Julia Sets
        # Create the threads based on each function the Julia Set Class
        self.circuit = circ
        timer['Julia_calculations'] = timeit.default_timer()
        self.res_1cn = set_1cn(c=sv_custom, z=z_arr.copy(), con=con_arr.copy(), div=div_arr.copy())
        self.res_2cn1 = set_2cn1(c=sv_list, z=z_arr.copy(), con=con_arr.copy(), div=div_arr.copy())
        self.res_2cn2 = set_2cn2(c=sv_list, z=z_arr.copy(), con=con_arr.copy(), div=div_arr.copy())
        timer['Julia_calculations'] = timeit.default_timer() - timer['Julia_calculations']

    def qf_animations(self, ax):
        # Secondly (a), generate the images based on the Julia set results
        timer['Animation'] = timeit.default_timer()

        # Plot Bloch sphere
        plot_bloch_multivector(self.circuit, filename=Path(temp_image_folder, "H.png"))
        ax[0].imshow(mpimg.imread(Path(temp_image_folder, "H.png")))
        ax[0].axis('off')
        ax[0].set_title('Bloch sphere', fontsize=20, pad=15.0)

        # Plot 1st Julia Fractal
        ax[1].imshow(self.res_1cn, cmap='magma')
        ax[1].axis('off')

        # Plot 2nd Julia Fractal
        ax[2].imshow(self.res_2cn1, cmap='magma')
        ax[2].set_title('3 types of Julia set fractals based on the superposition H-gate', fontsize=20, pad=15.0)
        ax[2].axis('off')

        # Plot 3rd Julia Fractal
        ax[3].figure.set_size_inches(16, 5)
        ax[3].imshow(self.res_2cn2, cmap='magma')
        ax[3].axis('off')
        ax[3].figure.supxlabel('ibm.biz/quantum-fractals-blog            ibm.biz/quantum-fractals', fontsize=20)

        # Snap a picture of the image outcome and close the plt object
        camera.snap()
        plt.close()
        timer['Animation'] = timeit.default_timer() - timer['Animation']

    def qf_images(self, ax):
        # Secondly (b), generate the images based on the Julia set results
        timer['Image'] = timeit.default_timer()

        # Plot Bloch sphere
        ax[0].imshow(mpimg.imread(Path(temp_image_folder, "H.png")))
        ax[0].axis('off')
        ax[0].set_title('Bloch sphere', fontsize=20, pad=15.0)

        # Plot 1st Julia Fractal
        ax[1].imshow(self.res_1cn, cmap='magma')
        ax[1].axis('off')

        # Plot 2nd Julia Fractal
        ax[2].imshow(self.res_2cn1, cmap='magma')
        ax[2].set_title('3 types of Julia set fractals based on the superposition H-gate', fontsize=20, pad=15.0)
        ax[2].axis('off')

        # Plot 3rd Julia Fractal
        ax[3].figure.set_size_inches(16, 5)
        ax[3].imshow(self.res_2cn2, cmap='magma')
        ax[3].axis('off')
        ax[3].figure.supxlabel('ibm.biz/quantum-fractals-blog            ibm.biz/quantum-fractals', fontsize=20)
        ax[3].figure.savefig(Path(temp_image_folder, "2cn2.png"))

        # Open in browser
        driver.get(default_image_url)
        plt.close()
        timer['Image'] = timeit.default_timer() - timer['Image']


# |
# | Running the script
# └───────────────────────────────────────────────────────────────────────────────────────────────────────
Fractal_quantum_circuit = FractalQuantumCircuit()

gif_fig, gif_ax = plt.subplots(1, 4, figsize=(20, 5))
camera = Camera(gif_fig)

for i in range(number_of_frames):
    try:
        # Firstly, get the complex numbers from the complex circuit
        timer['QuantumCircuit'] = timeit.default_timer()
        ccc = Fractal_quantum_circuit.get_quantum_circuit(frame_iteration=i)

        # Secondly, for the sake of transparency, the elements from the list are defined as separate variables
        circuit = ccc[1]
        statevector_custom = ccc[0]
        statevector_n_list = ccc[2]
        timer['QuantumCircuit'] = timeit.default_timer() - timer['QuantumCircuit']

        # Thirdly, run the animation and image creation
        img_fig, img_ax = plt.subplots(1, 4, figsize=(20, 5))
        QFI = QuantumFractalImages(sv_custom=statevector_custom, sv_list=statevector_n_list, circ=circuit)
        QFI.qf_animations(ax=gif_ax)
        QFI.qf_images(ax=img_ax)

        # Console logging output:
    except (NoSuchWindowException, WebDriverException):
        print("Error, Browser window closed during generation of images")
        raise traceback.format_exc()

# Quit the currently running driver and prepare for the animation
driver.quit()
print("Saving the current animation state in GIF")

anim = camera.animate(blit=True, interval=GIF_ms_intervals)
anim.save(f'{temp_image_folder}/1qubit_simulator_4animations_H_{number_of_frames}.gif', writer='pillow')
gif_url = f"{browser_file_path}/1qubit_simulator_4animations_H_{number_of_frames}.gif"

# Define a fresh instance of the ChromeDriver to retrieve the image
driver = WebClient(default_image_url).get_driver()  # ChromeDriver
driver.get(gif_url)

# check if the browser window is closed
while True:
    try:
        driver.find_element(By.TAG_NAME, 'body')
    except (NoSuchWindowException, WebDriverException):
        print("Error, Browser window closed, quitting the program")
        driver.quit()
        sys.exit()
