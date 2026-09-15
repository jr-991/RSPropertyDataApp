import tkinter as tk
import scraper
import tkinter.ttk as ttk

def GUI():
    root = tk.Tk()
    root.title("Real Estate Viewer")
    root.geometry("1280x720")

    frame = tk.Frame(root, width=1280, height=720)
    frame.pack(padx=10, pady=10)    

    topFrame = tk.Frame(frame)
    topFrame.pack(pady=10)

    # State selection dropdown
    stateDropdown = ttk.Combobox(topFrame, values=[state.value for state in scraper.State], state="readonly")
    stateDropdown.set("Select State")
    stateDropdown.pack(side='left', padx=(10, 5))

    # Page range selection
    labelLowPg = tk.Label(topFrame, text="Page")
    labelLowPg.pack(side='left', padx=(10, 5))
    lowPg = tk.Entry(topFrame, width=5)
    lowPg.insert(0, "1")
    lowPg.pack(side='left', padx=(5, 10))
    label = tk.Label(topFrame, text ="to")
    label.pack(side='left', padx=(5, 5))
    highPg = tk.Entry(topFrame, width=5)
    highPg.insert(0, "1")
    highPg.pack(side='left', padx=(5, 10))

    
    label = tk.Label(topFrame, text="Pull latest: ", font=("Arial", 16))
    label.pack(side='left', padx=(0, 5))

    # Button to call the pullData function
    pullButton = tk.Button(topFrame, text = "↓", command = lambda: pullData(stateDropdown.get(), lowPg.get(), highPg.get()))
    pullButton.pack(side='left')
    
    dataFrame = tk.Frame(frame, bg="lightgrey", width=1280, height=720)
    dataFrame.pack(fill='both', expand=True, pady=10, padx=10)
    
    root.mainloop()

def pullData(state, lowPg, highPg):
    scraper.fetch(state=scraper.State(state) if state != "Select State" else None, pgLow=int(lowPg) if lowPg else 1, pgHigh=int(highPg) if highPg else None)

if __name__ == "__main__":
    GUI()