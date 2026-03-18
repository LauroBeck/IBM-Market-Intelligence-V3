#include <iostream>
#include <iomanip>
#include <string>

struct Asset {
    std::string ticker;
    double price;
    std::string catalyst;
};

void executeHedge(double capital) {
    double hedge_amount = capital * 0.15;
    Asset nvda = {"NVDA", 181.93, "Vera Rubin / GTC 2026 Keynote"};
    Asset ibm = {"IBM", 256.11, "Quantum / Enterprise Agentic AI"};

    std::cout << "\n[STRATEGIC ACTION: CALCULATING HEDGE]" << std::endl;
    std::cout << "Rotating 15% (R$ " << std::fixed << std::setprecision(2) << hedge_amount << ") to USD Tech:" << std::endl;
    std::cout << "  -> BUY " << nvda.ticker << " @ $" << nvda.price << " (" << nvda.catalyst << ")" << std::endl;
    std::cout << "  -> BUY " << ibm.ticker << " @ $" << ibm.price << " (" << ibm.catalyst << ")" << std::endl;
}

int main() {
    std::cout << "--------------------------------------------------" << std::endl;
    std::cout << " MISSION: ASIA INTEL - RISK ENGINE (MAR 18, 2026) " << std::endl;
    std::cout << "--------------------------------------------------" << std::endl;

    double nifty_bank = 54850.00; // SIMULATED BREACH
    double bank_floor = 55000.00;
    double portfolio_value = 240000.00; // Target Mission Salary Base

    std::cout << "CHECKING NIFTY BANK: " << nifty_bank << std::endl;

    if (nifty_bank < bank_floor) {
        std::cout << "STATUS: !!! FLOOR BREACHED !!!" << std::endl;
        std::cout << "REASON: Goldman 6.5% GDP Cut / Hormuz Oil Spike" << std::endl;
        executeHedge(portfolio_value);
    } else {
        std::cout << "STATUS: RESILIENT. Maintain Long positions." << std::endl;
    }

    std::cout << "--------------------------------------------------" << std::endl;
    return 0;
}
