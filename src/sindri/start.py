#!/usr/bin/env python3
"""
Startup code for running the Sindri server mainloop as an application.
"""


def start_sindri(**serve_kwargs):
    print("Starting Sindri server...")
    import sindri.website.serve
    sindri.website.serve.start_serving_website(**serve_kwargs)


if __name__ == "__main__":
    start_sindri()
