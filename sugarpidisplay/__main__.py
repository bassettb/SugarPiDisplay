
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
if __name__ == "__main__":
	from sugarpidisplay.sugar_pi_app import SugarPiApp
	app = SugarPiApp()
	app.initialize()
	app.run()
