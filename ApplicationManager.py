from PyQt5.QtWidgets import QFileDialog
import wfdb, numpy as np, math, random
import pyqtgraph as pg
import Classes
class ApplicationManager:
    def __init__(self, ui_window, load_graph_1, load_graph_2, load_graph_3, compose_graph_1, compose_graph_2, compose_graph_3):
        # Graph Numbers Guide   1 -> Original -----  2 -> Reconstructed ----- 3 -> Difference
        self.ui_window = ui_window
        self.load_graph_1 = load_graph_1
        self.load_graph_2 = load_graph_2
        self.load_graph_3 = load_graph_3
        self.compose_graph_1 = compose_graph_1
        self.compose_graph_2 = compose_graph_2
        self.compose_graph_3 = compose_graph_3
        self.reconstructed_signal = None
        self.component_count = 0
        self.frequency = None
        self.sampled_points = None
        self.sampling_period = None
        self.loaded_signals = []
        self.current_loaded_signal = None
        self.COMPONENTS = []
        self.Composed_Signal = None


    def get_current_loaded_signal_slot(self, index):
        self.current_loaded_signal = self.loaded_signals[index]
        self.load_graph_1.clear()
        self.load_graph_1.plot(self.current_loaded_signal.X_Coordinates, self.current_loaded_signal.Y_Coordinates, pen = 'b')

        self.COMPONENTS = []

    def load_signal(self):
        File_Path, _ = QFileDialog.getOpenFileName(None, "Browse Signal", "", "All Files (*)")
        if File_Path:
            Record = wfdb.rdrecord(File_Path[:-4])
            Y_Coordinates = list(Record.p_signal[:1000, 0])
            X_Coordinates = list(np.arange(len(Y_Coordinates)))
            self.loaded_signals.append(Classes.Signal(X_Coordinates, Y_Coordinates))
            self.current_loaded_signal = self.loaded_signals[-1]
            if len(self.loaded_signals) > 1:
                Temporary_String = f"Signal {len(self.loaded_signals)}"
                self.ui_window.Load_Signals_ComboBox.addItem(Temporary_String)
                self.ui_window.Load_Signals_ComboBox.setCurrentIndex(len(self.loaded_signals) - 1)
            self.load_graph_1.clear()
            self.load_graph_1.plot(X_Coordinates, Y_Coordinates, pen = 'b')
            
            
    def plot_sine_wave(self):
        # Define the parameters of the sine wave
        frequency = 100  # Frequency in Hz
        duration = 1  # Duration in seconds
        sampling_rate = 1000  # Sampling rate in Hz (number of samples per second)

        # Generate the time values for one period of the sine wave
        t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

        # Generate the sine wave
        sine_wave = np.sin(2 * np.pi * frequency * t)

        # Plot the sine wave on load_graph_1
        self.load_graph_1.plot(t, sine_wave, pen='b')

        # Set the sine wave as the main signal
        self.main_signal = SignalClass.Signal(t.tolist(), sine_wave.tolist())
                
    def whittaker_shannon_interpolation(self, t, samples, T):
        # Calculate the sum of the product of the samples and the sinc function
        return sum(sample * np.sinc((t - k * T) / T) for k, sample in enumerate(samples))            
                
    def plot_samples(self, frequency):
        self.plot_sine_wave()
        freq = 100
        # Sample the signal at the given frequency
        self.sampled_points = self.main_signal.Y_Coordinates[::freq]
        self.sampling_period = 1 / freq

        # Plot the sampled points on load_graph_1
        self.load_graph_1.plot(self.main_signal.X_Coordinates[::freq], self.sampled_points, pen=None, symbol='o')
         # Reconstruct the signal and plot the difference
        self.reconstruct_signal()
        self.plot_difference()

    # Step 1: Sample the signal
    def plot_samples(self, sampling_frequency):
        self.frequency = sampling_frequency
        sampling_period = 1 / sampling_frequency #float result, not expected nor needed
        self.sampled_points = self.current_loaded_signal.X_Coordinates[::sampling_period] # I need to skip in the slicing tech using integer
        # Create a scatter plot item
        scatter_plot = pg.ScatterPlotItem()
        # Set the x and y coordinates of the scatter plot
        x_coordinates = np.arange(0, len(self.current_loaded_signal.X_Coordinates), int(1 / sampling_frequency))
        y_coordinates = self.sampled_points
        scatter_plot.setData(x_coordinates, y_coordinates)
        # Set the color of the scatter plot markers
        scatter_plot.setPen(pg.mkPen(color='r'))
        # Add the scatter plot item to the plot
        self.load_graph_1.plot.addItem(scatter_plot)

    # Step 2: Reconstruct the signal using Whittaker-Shannon interpolation formula
    def reconstruct_signal(sampled_points, sampling_frequency, original_length):
        time = np.arange(0, original_length)
        reconstructed_signal = np.zeros(original_length)
        for i in range(len(sampled_points)):
            reconstructed_signal += sampled_points[i] * np.sinc(time - i / sampling_frequency)
        return reconstructed_signal

    def Reconstruction_signal(self):
        pass
        #reconstructed_signal = reconstruct_signal(sampled_points, sampling_frequency, len(signal_data))

    def difference(self):
        pass
        # Step 3: Calculate the difference between the original and reconstructed signal
        #difference = signal_data - reconstructed_signal


    def add_noise(self, SNR_value, compose=False):
        if compose:
            signal_power = sum(y ** 2 for y in self.Composed_Signal.Y_Coordinates) / len(self.Composed_Signal.Y_Coordinates)
            noise_power = signal_power / (10 ** (SNR_value / 10))
            noise_std = math.sqrt(noise_power)
            noise = [random.gauss(0, noise_std) for _ in range(len(self.Composed_Signal.Y_Coordinates))]
            self.Composed_Signal.noisy_Y_Coordinates = [s + n for s, n in zip(self.Composed_Signal.Y_Coordinates, noise)]
            self.compose_graph_1.clear()
            self.compose_graph_1.plot(self.Composed_Signal.X_Coordinates,self.Composed_Signal.noisy_Y_Coordinates, pen='g')
            return
        signal_power = sum(y ** 2 for y in self.current_loaded_signal.Y_Coordinates) / len(self.current_loaded_signal.Y_Coordinates)
        noise_power = signal_power / (10**(SNR_value / 10))
        noise_std = math.sqrt(noise_power)
        noise = [random.gauss(0, noise_std) for _ in range(len(self.current_loaded_signal.Y_Coordinates))]
        self.current_loaded_signal.noisy_Y_Coordinates = [s + n for s, n in zip(self.current_loaded_signal.Y_Coordinates, noise)]
        self.load_graph_1.clear()
        self.load_graph_1.plot(self.current_loaded_signal.X_Coordinates, self.current_loaded_signal.noisy_Y_Coordinates, pen = 'b')

    


    def add_component(self):
        self.component_count += 1
        if self.component_count == 1:
            new_component = Classes.Component()
            self.COMPONENTS.append(new_component)
            return

        Temporary_String = f"Component {self.component_count}"
        self.ui_window.Compose_Components_ComboBox.addItem(Temporary_String)

        new_component = Classes.Component()
        self.COMPONENTS.append(new_component)


    def remove_component(self):
        if self.component_count == 1:
            return
        self.component_count -= 1
        selected_index = self.ui_window.Compose_Components_ComboBox.currentIndex()
        self.COMPONENTS.pop(selected_index)

        if selected_index == self.ui_window.Compose_Components_ComboBox.count() - 1:
            self.ui_window.Compose_Components_ComboBox.removeItem(selected_index)
        else:
            self.ui_window.Compose_Components_ComboBox.removeItem(selected_index)
            for index in range(self.ui_window.Compose_Components_ComboBox.count()):
                if self.ui_window.Compose_Components_ComboBox.itemText(index)[-1] != index + 1:
                    self.ui_window.Compose_Components_ComboBox.setItemText(index, f"Component {index+1}")

        self.update_signal()


    def update_sliders(self):
        selected_index = self.ui_window.Compose_Components_ComboBox.currentIndex()
        selected_component = self.COMPONENTS[selected_index]

        self.ui_window.Compose_Signal_Magnitude_Slider.setValue(selected_component.magnitude)
        self.ui_window.Compose_Signal_Frequency_Slider.setValue(selected_component.frequency)


    def update_magnitude(self):
        selected_index = self.ui_window.Compose_Components_ComboBox.currentIndex()
        selected_component = self.COMPONENTS[selected_index]

        selected_component.magnitude = self.ui_window.Compose_Signal_Magnitude_Slider.value()
        self.update_signal()


    def update_frequency(self):
        selected_index = self.ui_window.Compose_Components_ComboBox.currentIndex()
        selected_component = self.COMPONENTS[selected_index]

        selected_component.frequency = self.ui_window.Compose_Signal_Frequency_Slider.value()
        self.update_signal()


    def update_signal(self):

        signal_X = np.linspace(0, 1, 500)
        signal_Y = 0
        for component in self.COMPONENTS:
            signal_Y += component.magnitude * np.sin(2 * np.pi * component.frequency * signal_X)

        self.compose_graph_1.clear()
        self.compose_graph_1.plot(signal_X, signal_Y, pen='g')

        self.Composed_Signal = Classes.Signal(signal_X, signal_Y)