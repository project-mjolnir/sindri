#!/usr/bin/env python3
"""
Startup code for running the Sindri server mainloop as an application.
"""


def start_sindri(mode="test", verbose=0):
    print("Starting Sindri server...")
    import sindri.website.serve
    sindri.website.serve.start_serving_website(mode=mode, verbose=verbose)


if __name__ == "__main__":
    start_sindri()
