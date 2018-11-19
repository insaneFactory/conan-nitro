from conans import ConanFile, CMake, tools, VisualStudioBuildEnvironment
import os


class NitroConan(ConanFile):
	name = "nitro"
	version = "2.7"
	license = "LGPL-3.0"
	url = "https://github.com/insaneFactory/conan-nitro"
	description = "NITRO is a full-fledged, extensible library solution for reading and writing the National Imagery Transmission Format (NITF), a U.S. DoD standard format. It is written in cross-platform C, with bindings available for other languages."
	settings = "os", "compiler", "build_type", "arch"
	options = {"shared": [True, False]}
	default_options = "shared=True"
	
	def source(self):
		self.run("git clone https://github.com/mdaus/nitro.git")
		#self.run("cd nitro && git checkout static_shared")

	def build(self):
		pybin = "py -2" if self.settings.os == "Windows" else "python"
		installFolder = self.build_folder + "/install"
		bitness = "--enable-64bit" if self.settings.arch == "x86_64" else ""
		debugging = "--enable-debugging" if self.settings.build_type == "Debug" else ""
		
		configureStatic = "%s waf configure --libs-only --disable-java --disable-python --prefix=%s %s %s" % (pybin, installFolder, bitness, debugging)
		configureShared = "%s waf configure --libs-only --disable-java --disable-python --prefix=%s %s %s --shared" % (pybin, installFolder, bitness, debugging)
		buildAll = "%s waf install" % pybin
		buildNitfC = "%s waf install --target=nitf-c" % pybin
		
		if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
			vsenv = VisualStudioBuildEnvironment(self)
			with tools.environment_append(vsenv.vars):
				vcvars = tools.vcvars_command(self.settings)
				self.run("%s && %s" % (vcvars, configureStatic), cwd="nitro")
				if self.options.shared:
					self.run("%s && %s" % (vcvars, buildAll), cwd="nitro")
					self.run("%s && %s" % (vcvars, configureShared), cwd="nitro")
				self.run("%s && %s" % (vcvars, buildNitfC), cwd="nitro")
		else:
			self.run(configureStatic, cwd="nitro")
			if self.options.shared:
				self.run(buildAll, cwd="nitro")
				self.run(configureShared, cwd="nitro")
			self.run(buildNitfC, cwd="nitro")

	def package(self):
		self.copy("*.dll", dst="bin", src="install/bin")
		self.copy("*", dst="include", src="install/include")
		self.copy("*", dst="share", src="install/share")
		
		if self.settings.os == "Windows":
			for lib in ["nitf-c", "nrt-c"]:
				self.copy("*%s.dll" % lib, dst="bin", src="install/lib")
				self.copy("*%s.pdb" % lib, dst="bin", src="install/lib")
				self.copy("*%s.lib" % lib, dst="lib", src="install/lib")
		else:
			if self.options.shared:
				try:
					os.rename("install/lib/nitf-c.so", "install/lib/libnitf-c.so")
					os.rename("install/lib/nrt-c.so", "install/lib/libnrt-c.so")
				except:
					pass
				self.copy("libnitf-c.so", dst="lib", src="install/lib")
				self.copy("libnrt-c.so", dst="lib", src="install/lib")
			else:
				#self.copy("*cgm-c.a", dst="lib", src="install/lib")
				#self.copy("*j2k-c.a", dst="lib", src="install/lib")
				self.copy("*nitf-c.a", dst="lib", src="install/lib")
				self.copy("*nrt-c.a", dst="lib", src="install/lib")
			self.copy("*.dylib", dst="lib", src="install", keep_path=False)

	def package_info(self):
		self.cpp_info.libs = ["nitf-c", "nrt-c"]
		#if not self.options.shared:
		#	self.cpp_info.libs.append("cgm-c")
		#	self.cpp_info.libs.append("j2k-c")

