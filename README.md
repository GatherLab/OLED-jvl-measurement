<h1 align="center">
  GatherLab OLED Measurement Setup
</h1>

<p align="center">
   <a href="https://github.com/GatherLab/OLED-jvl-measurement/commits/" title="Last Commit"><img src="https://img.shields.io/github/last-commit/GatherLab/OLED-jvl-measurement?style=flat"></a>
   <a href="https://github.com/GatherLab/OLED-jvl-measurement/issues" title="Open Issues"><img src="https://img.shields.io/github/issues/GatherLab/OLED-jvl-measurement?style=flat"></a>
   <a href="./LICENSE" title="License"><img src="https://img.shields.io/github/license/GatherLab/OLED-jvl-measurement"></a>
</p>

<p align="center">
  <a href="#development">Setup</a> •
  <a href="#hardware">Hardware</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#licensing">Licensing</a>
</p>

The goal of this project is to develop an easy to use interface for the investigation of organic leds (OLEDs). The measurements may or may not comprise current-voltage-luminance or spectral measurements. Additionally, an angle resolved spectrum of the OLED under investigation is made possible. Ultimately, the program should be easily usable and facilitate measurement and evaluation of classic OLED characterisation.

<!-- ![Figure 1: Example of the interface]("link" "Figure 1: UI Screens for Apple iOS") -->

## Setup

### First Setup

Setup a python environment with your favourite virtual environment management tool. The following step by step guide assumes that the user wants to use the since python 3.3 recommended software venv that ships with python on a windows machine.

1. Clone project folder to your local machine
2. Change e.g. with windows power shell into the project folder
3. Generate a virtual environement with the name "venv"

```terminal
py -m venv venv
```

4. Activate the new environement

```
Set-ExecutionPolicy Unrestricted -Scope Process
.\venv\Scripts\activate
```

5. Install required packages from requirements.txt (this assumes that pip is activated on your machine)

```
pip install -r requirements.txt
```

6. Install thorlabs_apt to obtain apt.dll driver (Follow https://github.com/qpit/thorlabs_apt for correct installation guidelines. For us, it only worked when apt.dll was copied to the Windows/System32 folder.
7. Ensure that libusb-1.0.lib driver is installed for detecting usb hardware (Follow https://stackoverflow.com/questions/33972145/pyusb-on-windows-8-1-no-backend-available-how-to-install-libusb for more on this)
8. Install NI-visa from website: https://www.ni.com/de-de/support/downloads/drivers/download.ni-visa.html#346210
9. Install Keithley drivers from website: https://de.tek.com/source-measure-units/2450-software-6 (prerequisit: NI-visa)
10. On the Keithley source meter (for specs see below) the command set on the Keithley has to be changed to SCPI
11. Execute the main.py file to start the program

```terminal
python3 main.py
```

### Development

- Python formatter: black

## Hardware

The different OLED pixels are activated with and Arduino UNO and a relay shield. Power is provided by a Keithley source unit that also allows the simultaneous measurement of applied voltage and drawn current. Photodiode voltage is measured with a Keithley Multimeter. Spectra are measured with an Ocean Spectrometer. For the goniometer setup, the rotation of the sample is done with a Thorlab motor. All items needed for the setup are listed below.

| Item                | Brand    | Model Number      |
| ------------------- | -------- | ----------------- |
| Ocean Spectrometer  | Ocean    | ?                 |
| Arduino UNO         | Arduino  | ?                 |
| Keithley Source     | Keithley | ?                 |
| Keithley Multimeter | Keithley | ?                 |
| Thorlab Motor       | Thorlab  | ? # Documentation |

## Documentation

### Setup (Current Tester)

Here the basic information about the measured batch must be provided that are

- The folder path used to save the measured data and the configuration files (with measurement parameters)
- A short name that characterises the batch well
- The device number of the currently measured device

After these parameters are set (that are valid globally over the entire program) a current testing can be done to test which pixels of the OLED work. The idea is to just select pixels on the left side (multiple pixels can be selected by clicking on them). The additional options given shall facilitate the testing. Those are

- select all pixels
- unselect all pixels
- pre-bias all pixels (to a predefined bias as e.g. - 2 V)
- auto test all pixels. I don't know yet exactly how to implement this but one could, for instance, simply think about a current threshold that must be reached at a certain predefined voltage. If it isn't the pixel is defined as not working.

The current reading can be seen on the large LCD style widget next to the pixel selection. This is not really necessary since it can also be read from the Keithley of course but may facilitate operation.

The option below allows to change the voltage to test the pixels provided over the Keithley.

Below that the user is asked to provide some short of brief documentation of the batch for easier tracking of what is going on. I was thinking of comments like:

- "OLED configuration: Ag - MoO3 - SpiroTTB + F6TCNNQ - NPB - MADN + TBPe - Balq - Bphen + CsO - Ag"
- "Most devices do not work possibly due to ..."
- "[!] The software always returns an error when measuring pixel 8 possibly due to ..."

This shall be optional but may facilitate future error tracking and improvement of the software as well as tracking down problems with the OLEDs or the sample holder.

### Autotube JVL

Measurement parameters can be selected on the right side. Pixels that worked in the Setup section are automatically selected. The user still has the possibility to exclude those pixels. The measurement is started using the "Start Measurement" button. A progress bar in the bottom status bar shows the progress of the measurement. The measured current and PD voltage are plotted directly on the center graph. Any problem messages are displayed in the bottom statusbar (that by default say "Ready")

### Spectrum

Tab to measure spectrum of an OLED pixel. It is unclear if this can be easily done to me, since I don't know about the api of the spectrum. Should, however, in principle be possible because it is probably also used for the goniometer measurements. The idea is to simply allow the user to measure the spectrum from the program as well instead of changing to the OceanView software. This could then be even combined with a direct calculation of the performance parameters if a spectrum was already measured. If it wasn't the autotube JVL just shows the current and photodiode voltage.

For the measurement the user only has to provide the pixel that shall be measured and the voltage that shall be applied for the measurement. One could also think about a seperate background measurement button but we could also make the separate measurement of a background spectrum obsolete by turning the OLED off automatically after the measurement was done and then subtract the spectrum automatically.

### Goniometer

Current motor/stage position is displayed visually on the top right including a angle reading. The offset angle can be changed manually for sample adjustment (by explicitly clicking on the move button to prevent unwanted movements).
If the sample is setup in the goniometer setup, the scanning parameters including the overall scanning angle (starting from 0°) can be entered. Additional options to do a PL instead of an EL measurement as well as entering a constant current instead of a constant voltage are provided.

Are there any specific parameters that should only be provided for EL/PL measurements?

Again the pixel of interest can be selected. However, only one because only one can be measured at once. The measurement can be started using a start measurement button.

The progress of the measurement can be seen via the progress bar in the status bar, on the plot on the left (the nature of which is not clearly defined yet) or by looking at the current stage position at the top.

### Additional/Global Settings

In the top menubar there is are two options:

- File
  - Load Measurement Parameters
  - Save Measurement Parameters
- Settings
  - Options
  - Help
  - Open Log

The idea is that measurement parameters can be saved and loaded for later measurements and so that not all the parameters have to be entered again all the time (although standard parameters shall be provided).

The settings tab is not yet clearly defined although it shall link to the documentation of the software (via Help) and allow to open the log file that logs possible errors occurring with the program. I don't know yet what the options tab contains but this might contain some global options that are only seldomly touched. If it is not necessary after all we can just delete it.

#### Parameters for global settings

- Keithley and arduino addresses
- photodiode gain
