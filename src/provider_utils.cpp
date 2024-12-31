#include "providers.h"

ProviderContainer::const_iterator ProviderUtils::find_by_name(const ProviderContainer& providers, const std::string& name) {
    return providers.find(name);
}

std::vector<ProviderConfig> ProviderUtils::get_local_providers(const ProviderContainer& providers) {
    std::vector<ProviderConfig> result;
    auto& index = providers.get<2>(); // local_only index
    auto range = index.equal_range(true);
    for (auto it = range.first; it != range.second; ++it) {
        result.push_back(*it);
    }
    return result;
}

std::vector<ProviderConfig> ProviderUtils::get_streaming_providers(const ProviderContainer& providers) {
    std::vector<ProviderConfig> result;
    auto& index = providers.get<3>(); // streaming index
    auto range = index.equal_range(true);
    for (auto it = range.first; it != range.second; ++it) {
        result.push_back(*it);
    }
    return result;
}
