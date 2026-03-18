#ifndef INCLUDED_MOCK_BLPAPI
#define INCLUDED_MOCK_BLPAPI
#include <iostream>
#include <string>

namespace BloombergLP { namespace blpapi {
    struct Event { enum EventType { RESPONSE, SUBSCRIPTION_DATA }; EventType eventType() const { return RESPONSE; } };
    struct Message { 
        void print(std::ostream& os) const { 
            os << "  [SIM] GDPIYOY Index (Goldman): 6.5%\n"
               << "  [SIM] USDINR Curncy (Record Low): 92.47\n"
               << "  [SIM] INRREPO Index (RBI Pause): 5.25%\n"
               << "  [SIM] NSEBANK Index: 56,582.10 (Resilient)";
        }
    };
    struct MessageIterator {
        bool d_done = false;
        MessageIterator(const Event& e) {}
        bool isValid() { return !d_done; }
        Message message() { d_done = true; return Message(); }
        void next() { d_done = true; }
    };
    struct Request { void appendValue(const char* k, const char* v) {} };
    struct Service { Request createRequest(const char* n) { return Request(); } };
    struct SessionOptions { void setServerHost(const char* h) {} void setServerPort(int p) {} };
    struct Session {
        Session(const SessionOptions& o) {}
        bool start() { return true; }
        bool openService(const char* s) { return true; }
        Service getService(const char* s) { return Service(); }
        void sendRequest(const Request& r) {}
        Event nextEvent() { return Event(); }
    };
}}
#endif
