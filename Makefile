# Makefile with a collection of common commands for PyDjinni development

cmake_configure:
	cmake -B cmake-build

cmake_build: cmake_configure
	cmake --build cmake-build

build:
	python -m build

pytest:
	pytest

test_support_lib: cmake_build
	ctest --test-dir cmake-build --output-on-failure

test: pytest test_support_lib


