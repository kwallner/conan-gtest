import os
from conans import ConanFile, tools, CMake

class ConanProject(ConanFile):
    name = "gtest"
    version = "1.10.0"
    _sha256_checksum = "9dc9157a9a1551ec7a7e43daea9a694a0bb5fb8bec81235d8a1e6ef64c716dcb"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { "shared" : False, "fPIC" : True }
    url = "http://github.com/kwallner/conan-gtest"
    license = 'BSD 3-clause "New" or "Revised" License'
    description = "Google's C++ test framework"
    no_copy_source = True
     
    def configure(self):
        if self.settings.compiler == "Visual Studio" and self.settings.compiler.runtime == "MT" and self.settings.build_type == "Debug":
            self.settings.compiler.runtime = "MTd"

    def source(self):
        # Unpack and rename
        tools.download("https://github.com/google/googletest/archive/release-%s.tar.gz" % self.version, "googletest-release-%s.tar.gz" % self.version, sha256=self._sha256_checksum)
        tools.unzip("googletest-release-%s.tar.gz" % self.version)
        os.remove("googletest-release-%s.tar.gz" % self.version)
        tools.replace_in_file("googletest-release-%s/googletest/cmake/internal_utils.cmake" % self.version, 'DEBUG_POSTFIX "d"', 'DEBUG_POSTFIX ""')
                    
    def build(self):
        cmake = CMake(self)
        if self.settings.compiler == "Visual Studio" and "MD" in str(self.settings.compiler.runtime):
            cmake.definitions["gtest_force_shared_crt"] = "ON"

        cmake.definitions["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"
        cmake.definitions["GTEST_CREATE_SHARED_LIBRARY"] = "ON" if self.options.shared else "OFF"
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = "ON" if self.options.fPIC or self.options.shared else "OFF"
        cmake.definitions["CMAKE_VERBOSE_MAKEFILE"] = "ON"
        cmake.definitions["BUILD_GTEST"] = "ON"
        cmake.definitions["BUILD_GMOCK"] = "ON"

        # No debug postfix
        cmake.definitions["CMAKE_DEBUG_POSTFIX"] = ""
        
        # Windows settings
        if self.settings.os == "Windows":
            cmake.definitions["gtest_force_shared_crt"] = "ON"
            if self.settings.compiler == "gcc":
                cmake.definitions["gtest_disable_pthreads"] = True

        cmake.configure(source_dir="%s/googletest-release-%s" % (self.source_folder, self.version))
        cmake.build()
        cmake.install()

    def package(self):
        # Copy the license files
        self.copy("LICENSE", src="googletest-release-%s" % self.version, dst=".", keep_path=False)
        self.copy("README.md", dst=".", keep_path=False)

    def package_info(self):
        self.cpp_info.name = "GTest"
        self.cpp_info.components["libgtest"].libs = ["gtest"] 
        self.cpp_info.components["gtest_main"].libs = ["gtest_main"]
        self.cpp_info.components["gtest_main"].requires = ["libgtest"]
        self.cpp_info.components["gmock"].libs = ["gmock"] 
        self.cpp_info.components["gmock"].requires = ["libgtest"]
        self.cpp_info.components["gmock_main"].libs = ["gmock_main"]
        self.cpp_info.components["gmock_main"].requires = ["gmock"]

        if self.settings.os == "Linux":
            self.cpp_info.components["libgtest"].system_libs.append("pthread")
        
        if self.options.shared:
            self.cpp_info.components["libgtest"].defines.append("GTEST_LINKED_AS_SHARED_LIBRARY=1")

        if float(str(self.settings.compiler.version)) >= 15 and self.settings.compiler == "Visual Studio":
            self.cpp_info.components["libgtest"].defines.append("GTEST_LANG_CXX11=1")
