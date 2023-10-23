from PyQt5.QtWidgets import QFileDialog
import wfdb, numpy as np
import SignalClass
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
        self.main_signal = None
        self.noisy_signal = None


    def load_signal(self):
        File_Path, _ = QFileDialog.getOpenFileName(None, "Browse Signal", "", "All Files (*)")
        if File_Path:
            Record = wfdb.rdrecord(File_Path[:-4])
            Y_Coordinates = list(Record.p_signal[:1000, 0])
            X_Coordinates = list(np.arange(len(Y_Coordinates)))
            self.main_signal = SignalClass.Signal(X_Coordinates, Y_Coordinates, 'r')


            self.load_graph_1.plot(X_Coordinates, Y_Coordinates, pen = 'b')

    def add_noise(self, SNR_value):
        signal_power = np.mean(self.main_signal.Y_Coordinates) ** 2
        noise_power = signal_power / SNR_value
        noise = np.random.normal(0, np.sqrt(noise_power), len(self.main_signal.Y_Coordinates))
        self.noisy_signal = SignalClass.Signal(self.main_signal.X_Coordinates, self.main_signal.Y_Coordinates + noise)
        self.load_graph_2.plot(self.noisy_signal.X_Coordinates, self.noisy_signal.Y_Coordinates, pen = 'b')