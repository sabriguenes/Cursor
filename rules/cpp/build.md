---
description: Build C++ projects with CMake
---

# Build Command

Build the project using CMake presets.

## Instructions

1. **Check for CMake presets:**

```bash
cmake --list-presets
```

2. **If presets exist, use them:**

```bash
cmake --preset <preset-name>
cmake --build --preset <preset-name>
```

3. **If no presets, use standard out-of-source build:**

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

4. **For specific compilers:**

| Compiler | CMake Generator |
|----------|-----------------|
| MSVC | `-G "Visual Studio 17 2022"` |
| GCC | `-DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++` |
| Clang | `-DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++` |

## Output

Build artifacts will be in the `build/` directory (or as specified by presets).

---

*Based on [Vinnie Falco's](https://github.com/vinniefalco) build command from [cppalliance/coro-io-context](https://github.com/cppalliance/coro-io-context)*
