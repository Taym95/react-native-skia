# Copyright 2016 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import contextlib
import os
import sys

from pylib import constants

DIR_SOURCE_ROOT = os.environ.get(
    'CHECKOUT_SOURCE_ROOT',
    os.path.abspath(os.path.join(os.path.dirname(__file__),
                                 os.pardir, os.pardir, os.pardir, os.pardir)))

BUILD_COMMON_PATH = os.path.join(
    DIR_SOURCE_ROOT, 'build', 'util', 'lib', 'common')

# third-party libraries
ANDROID_PLATFORM_DEVELOPMENT_SCRIPTS_PATH = os.path.join(
    DIR_SOURCE_ROOT, 'third_party', 'android_platform', 'development',
    'scripts')
BUILD_PATH = os.path.join(DIR_SOURCE_ROOT, 'build')
DEVIL_PATH = os.path.join(
    DIR_SOURCE_ROOT, 'third_party', 'catapult', 'devil')
TRACING_PATH = os.path.join(
    DIR_SOURCE_ROOT, 'third_party', 'catapult', 'tracing')

@contextlib.contextmanager
def SysPath(path, position=None):
  if position is None:
    sys.path.append(path)
  else:
    sys.path.insert(position, path)
  try:
    yield
  finally:
    if sys.path[-1] == path:
      sys.path.pop()
    else:
      sys.path.remove(path)


# Map of CPU architecture name to (toolchain_name, binprefix) pairs.
# TODO(digit): Use the build_vars.txt file generated by gn.
_TOOL_ARCH_MAP = {
  'arm': ('arm-linux-androideabi-4.9', 'arm-linux-androideabi'),
  'arm64': ('aarch64-linux-android-4.9', 'aarch64-linux-android'),
  'x86': ('x86-4.9', 'i686-linux-android'),
  'x86_64': ('x86_64-4.9', 'x86_64-linux-android'),
  'x64': ('x86_64-4.9', 'x86_64-linux-android'),
  'mips': ('mipsel-linux-android-4.9', 'mipsel-linux-android'),
}

# Cache used to speed up the results of ToolPath()
# Maps (arch, tool_name) pairs to fully qualified program paths.
# Useful because ToolPath() is called repeatedly for demangling C++ symbols.
_cached_tool_paths = {}


def ToolPath(tool, cpu_arch):
  """Return a fully qualifed path to an arch-specific toolchain program.

  Args:
    tool: Unprefixed toolchain program name (e.g. 'objdump')
    cpu_arch: Target CPU architecture (e.g. 'arm64')
  Returns:
    Fully qualified path (e.g. ..../aarch64-linux-android-objdump')
  Raises:
    Exception if the toolchain could not be found.
  """
  tool_path = _cached_tool_paths.get((tool, cpu_arch))
  if tool_path:
    return tool_path

  toolchain_source, toolchain_prefix = _TOOL_ARCH_MAP.get(
      cpu_arch, (None, None))
  if not toolchain_source:
    raise Exception('Could not find tool chain for ' + cpu_arch)

  toolchain_subdir = (
      'toolchains/%s/prebuilt/linux-x86_64/bin' % toolchain_source)

  tool_path = os.path.join(constants.ANDROID_NDK_ROOT,
                           toolchain_subdir,
                           toolchain_prefix + '-' + tool)

  _cached_tool_paths[(tool, cpu_arch)] = tool_path
  return tool_path


def GetAaptPath():
  """Returns the path to the 'aapt' executable."""
  return os.path.join(constants.ANDROID_SDK_TOOLS, 'aapt')