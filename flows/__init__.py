"""Reusable end-to-end flows.

A *flow* composes page objects and validations into a complete journey that a
test can call in one line. It sits above ``pages/`` and ``validations/`` and
below ``tests/``:

    config/      what is expected
    pages/       how to reach and locate it
    validations/ what must be true
    flows/       a whole journey, reusable from any test   <-- this layer
    tests/       which journeys to run, and their markers

Each flow is independent of the others. ``LogoutFlow`` assumes only that a
user is authenticated - never how that happened, nor what was tested in
between - so any future test can end with it:

    login  ->  create a dealer  ->  validate it  ->  logout
"""
