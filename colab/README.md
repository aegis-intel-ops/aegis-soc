# Aegis Colab Worker

This folder contains scripts to run on Google Colab to provide GPU power to your Aegis SOC.

## 🚀 How to Run

1.  Open [Google Colab](https://colab.research.google.com/).
2.  Create a **New Notebook**.
3.  **Runtime > Change runtime type > T4 GPU**.
4.  Copy the contents of `mist_v2_worker.py` into a cell.
5.  Update the `PASSWORD` variable if you changed your Admin password.
6.  Run the cell.

The worker will start polling your SOC for jobs!

## MIST / PhotoGuard Setup (Advanced)

To actually run MIST, add this to the top of the notebook:

```bash
!git clone https://github.com/checksum/mist-v2.git
!pip install -r mist-v2/requirements.txt
```

And modify the `process_job` function to call the mist script.
