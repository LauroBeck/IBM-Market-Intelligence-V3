CXX = g++
# Use the exported variable or a direct path
CXXFLAGS = -O3 -I$(BLPAPI_ROOT)/include
LDFLAGS = -L$(BLPAPI_ROOT)/lib -lblpapi3_64 -Wl,-rpath,$(BLPAPI_ROOT)/lib

all: market_mission

market_mission: market_mission.cpp
	$(CXX) $(CXXFLAGS) market_mission.cpp $(LDFLAGS) -o market_mission

clean:
	rm -f market_mission
