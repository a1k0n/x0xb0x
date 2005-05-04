from Globals import *
from pattern import Pattern
from GraphicalInterface import *

class View:

    def __init__(self, controller):
        self.controller = controller

        # Create an instance of our customized Frame class - the GUI. (this is the view)
        self.mainWindow = MainWindow(self.controller, -1, "x0xb0x c0ntr0l")
        self.currentPattern = None

        
    def updateStatusText(self, string):
        self.mainWindow.StatusBar.SetStatusText(string, 0)

    def updateCurrentPattern(self, pattern):
        grid = self.mainWindow.patternGrid

        for i in range(0, pattern.length):

            if pattern.note(i).rest:
                grid.SetCellValue(0, i, '')
                grid.SetCellValue(1, i, '')
                grid.SetCellValue(2, i, '')

            else:    
                grid.SetCellValue(0, i, chr(pattern.note(i).note))
                grid.SetCellValue(1, i, 'O')
                
                efx = ''
                if pattern.note(i).accent:
                    efx += 'A'
                elif pattern.note(i).slide:
                    efx += 'S'
                elif pattern.note(i).transpose == TRANSPOSE_UP:
                    efx += 'U'
                elif pattern.note(i).transpose == TRANSPOSE_DOWN:
                    efx += 'D'
                grid.SetCellValue(2, i, efx)


        for i in range(pattern.length, 16):
            grid.SetCellValue(0, i, '')
            grid.SetCellValue(1, i, '')
            grid.SetCellValue(2, i, '')



        
