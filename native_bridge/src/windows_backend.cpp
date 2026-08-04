#include "bridge/windows_backend.hpp"

#include <algorithm>
#include <cctype>
#include <cwctype>
#include <memory>
#include <string>
#include <vector>

#if defined(_WIN32)
#include <comdef.h>
#include <mmdeviceapi.h>
#include <propsys.h>
#include <endpointvolume.h>
#include <wrl/client.h>
#include <windows.h>

namespace bridge {

namespace {

using Microsoft::WRL::ComPtr;

// Device property key we need. Normally exposed by <functiondiscoverykeys_devpkey.h>,
// which is brittle under modern MSVC (/permissive-); we declare the one key used here
// directly as a file-local constant so no fragile GUID header is required.
const PROPERTYKEY kPKEY_Device_FriendlyName = {
    {0xA45C254E, 0xDF1C, 0x4EFD, {0x80, 0x20, 0x67, 0xD1, 0x46, 0xA8, 0x50, 0xE0}},
    14};

constexpr CLSID CLSID_PolicyConfigClient = {0x870af99c, 0x171d, 0x4f9e, {0xaf, 0x0d, 0xe6, 0x3d, 0xf4, 0x0c, 0x2b, 0xc9}};

MIDL_INTERFACE("F8679F50-850A-41CF-9C72-430F290290C8")
IPolicyConfig : public IUnknown {
    virtual HRESULT STDMETHODCALLTYPE GetMixFormat(LPCWSTR, WAVEFORMATEX**) = 0;
    virtual HRESULT STDMETHODCALLTYPE GetDeviceFormat(LPCWSTR, INT, WAVEFORMATEX**) = 0;
    virtual HRESULT STDMETHODCALLTYPE SetDeviceFormat(LPCWSTR, WAVEFORMATEX*, WAVEFORMATEX*) = 0;
    virtual HRESULT STDMETHODCALLTYPE GetProcessingPeriod(LPCWSTR, INT, PINT64, PINT64) = 0;
    virtual HRESULT STDMETHODCALLTYPE SetProcessingPeriod(LPCWSTR, PINT64) = 0;
    virtual HRESULT STDMETHODCALLTYPE GetShareMode(LPCWSTR, void*) = 0;
    virtual HRESULT STDMETHODCALLTYPE SetShareMode(LPCWSTR, void*) = 0;
    virtual HRESULT STDMETHODCALLTYPE GetPropertyValue(LPCWSTR, const PROPERTYKEY&, PROPVARIANT*) = 0;
    virtual HRESULT STDMETHODCALLTYPE SetPropertyValue(LPCWSTR, const PROPERTYKEY&, const PROPVARIANT*) = 0;
    virtual HRESULT STDMETHODCALLTYPE SetDefaultEndpoint(LPCWSTR, ERole) = 0;
    virtual HRESULT STDMETHODCALLTYPE SetEndpointVisibility(LPCWSTR, BOOL) = 0;
};

class ComInit final {
   public:
    ComInit() : hr_(CoInitializeEx(nullptr, COINIT_MULTITHREADED)) {}
    ~ComInit() {
        if (SUCCEEDED(hr_)) {
            CoUninitialize();
        }
    }

    bool ok() const { return SUCCEEDED(hr_) || hr_ == RPC_E_CHANGED_MODE; }

   private:
    HRESULT hr_;
};

struct DeviceRecord {
    std::wstring id;
    std::wstring friendlyName;
};

std::wstring utf8ToWide(const std::string& text) {
    if (text.empty()) {
        return {};
    }

    const int length = MultiByteToWideChar(CP_UTF8, 0, text.c_str(), -1, nullptr, 0);
    std::wstring output(length > 0 ? length - 1 : 0, L'\0');
    if (length > 0) {
        MultiByteToWideChar(CP_UTF8, 0, text.c_str(), -1, output.data(), length);
    }
    return output;
}

std::string wideToUtf8(const std::wstring& text) {
    if (text.empty()) {
        return {};
    }

    const int length = WideCharToMultiByte(CP_UTF8, 0, text.c_str(), -1, nullptr, 0, nullptr, nullptr);
    std::string output(length > 0 ? length - 1 : 0, '\0');
    if (length > 0) {
        WideCharToMultiByte(CP_UTF8, 0, text.c_str(), -1, output.data(), length, nullptr, nullptr);
    }
    return output;
}

bool containsCaseInsensitive(const std::string& value, const std::string& needle) {
    std::string lhs = value;
    std::string rhs = needle;
    std::transform(lhs.begin(), lhs.end(), lhs.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    std::transform(rhs.begin(), rhs.end(), rhs.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    return lhs.find(rhs) != std::string::npos;
}

std::wstring getFriendlyName(IMMDevice* device) {
    ComPtr<IPropertyStore> store;
    if (FAILED(device->OpenPropertyStore(STGM_READ, store.GetAddressOf())) || !store) {
        return {};
    }

    PROPVARIANT value;
    PropVariantInit(&value);
    std::wstring friendlyName;
    if (SUCCEEDED(store->GetValue(kPKEY_Device_FriendlyName, &value)) && value.vt == VT_LPWSTR && value.pwszVal) {
        friendlyName = value.pwszVal;
    }
    PropVariantClear(&value);
    return friendlyName;
}

std::wstring getDeviceId(IMMDevice* device) {
    LPWSTR id = nullptr;
    std::wstring output;
    if (SUCCEEDED(device->GetId(&id)) && id) {
        output = id;
        CoTaskMemFree(id);
    }
    return output;
}

std::vector<DeviceRecord> enumerateDevices() {
    std::vector<DeviceRecord> devices;

    ComPtr<IMMDeviceEnumerator> enumerator;
    if (FAILED(CoCreateInstance(CLSID_MMDeviceEnumerator, nullptr, CLSCTX_ALL, __uuidof(IMMDeviceEnumerator), reinterpret_cast<void**>(enumerator.GetAddressOf()))) || !enumerator) {
        return devices;
    }

    ComPtr<IMMDeviceCollection> collection;
    if (FAILED(enumerator->EnumAudioEndpoints(eRender, DEVICE_STATE_ACTIVE, collection.GetAddressOf())) || !collection) {
        return devices;
    }

    UINT count = 0;
    if (FAILED(collection->GetCount(&count))) {
        return devices;
    }

    for (UINT index = 0; index < count; ++index) {
        ComPtr<IMMDevice> device;
        if (FAILED(collection->Item(index, device.GetAddressOf())) || !device) {
            continue;
        }

        auto id = getDeviceId(device);
        auto friendlyName = getFriendlyName(device);
        if (!id.empty() && !friendlyName.empty()) {
            devices.push_back({std::move(id), std::move(friendlyName)});
        }
    }

    return devices;
}

bool isEarbudDevice(const std::wstring& deviceName) {
    std::wstring lower = deviceName;
    std::transform(lower.begin(), lower.end(), lower.begin(), [](wchar_t ch) { return static_cast<wchar_t>(std::towlower(ch)); });
    return lower.find(L"bluetooth") != std::wstring::npos || lower.find(L"headphone") != std::wstring::npos ||
           lower.find(L"earbud") != std::wstring::npos || lower.find(L"buds") != std::wstring::npos ||
           lower.find(L"airpods") != std::wstring::npos;
}

bool isVirtualHubDevice(const std::wstring& deviceName) {
    std::wstring lower = deviceName;
    std::transform(lower.begin(), lower.end(), lower.begin(), [](wchar_t ch) { return static_cast<wchar_t>(std::towlower(ch)); });
    return lower.find(L"voicemeeter") != std::wstring::npos || lower.find(L"vb-audio") != std::wstring::npos ||
           lower.find(L"virtual cable") != std::wstring::npos || lower.find(L"cable input") != std::wstring::npos ||
           lower.find(L"loopback") != std::wstring::npos || lower.find(L"aggregate") != std::wstring::npos ||
           lower.find(L"multi-output") != std::wstring::npos;
}

ComPtr<IPolicyConfig> createPolicyConfig() {
    IPolicyConfig* policy = nullptr;
    if (FAILED(CoCreateInstance(CLSID_PolicyConfigClient, nullptr, CLSCTX_ALL, __uuidof(IPolicyConfig), reinterpret_cast<void**>(&policy)))) {
        return nullptr;
    }

    ComPtr<IPolicyConfig> result;
    result.Attach(policy);
    return result;
}

}  // namespace

WindowsBackend::WindowsBackend() = default;

bool WindowsBackend::isEarbudDevice(const std::string& deviceName) const {
    return containsCaseInsensitive(deviceName, "bluetooth") || containsCaseInsensitive(deviceName, "headphone") ||
           containsCaseInsensitive(deviceName, "earbud") || containsCaseInsensitive(deviceName, "buds") ||
           containsCaseInsensitive(deviceName, "airpods");
}

bool WindowsBackend::isVirtualHubDevice(const std::string& deviceName) const {
    return containsCaseInsensitive(deviceName, "voicemeeter") || containsCaseInsensitive(deviceName, "vb-audio") ||
           containsCaseInsensitive(deviceName, "virtual cable") || containsCaseInsensitive(deviceName, "cable input") ||
           containsCaseInsensitive(deviceName, "loopback") || containsCaseInsensitive(deviceName, "aggregate") ||
           containsCaseInsensitive(deviceName, "multi-output");
}

std::vector<SinkInfo> WindowsBackend::listSinks() {
    ComInit com;
    std::vector<SinkInfo> sinks;
    if (!com.ok()) {
        return sinks;
    }

    for (const auto& device : enumerateDevices()) {
        const auto name = wideToUtf8(device.friendlyName);
        const auto id = wideToUtf8(device.id);
        if (!name.empty() && !id.empty() && isEarbudDevice(name)) {
            sinks.push_back({name, name, id});
        }
    }
    return sinks;
}

void WindowsBackend::setVolume(const std::string& sinkName, int volumePercent) {
    ComInit com;
    if (!com.ok()) {
        return;
    }

    auto targetName = utf8ToWide(sinkName);
    ComPtr<IMMDeviceEnumerator> enumerator;
    if (FAILED(CoCreateInstance(CLSID_MMDeviceEnumerator, nullptr, CLSCTX_ALL, __uuidof(IMMDeviceEnumerator), reinterpret_cast<void**>(enumerator.GetAddressOf()))) || !enumerator) {
        return;
    }

    ComPtr<IMMDeviceCollection> collection;
    if (FAILED(enumerator->EnumAudioEndpoints(eRender, DEVICE_STATE_ACTIVE, collection.GetAddressOf())) || !collection) {
        return;
    }

    UINT count = 0;
    if (FAILED(collection->GetCount(&count))) {
        return;
    }

    for (UINT index = 0; index < count; ++index) {
        ComPtr<IMMDevice> device;
        if (FAILED(collection->Item(index, device.GetAddressOf())) || !device) {
            continue;
        }

        auto id = getDeviceId(device);
        auto friendlyName = getFriendlyName(device);
        if ((id == targetName) || (friendlyName == targetName)) {
            ComPtr<IAudioEndpointVolume> endpointVolume;
            if (SUCCEEDED(device->Activate(__uuidof(IAudioEndpointVolume), CLSCTX_ALL, nullptr, reinterpret_cast<void**>(endpointVolume.GetAddressOf()))) && endpointVolume) {
                endpointVolume->SetMasterVolumeLevelScalar(static_cast<float>(volumePercent) / 100.0f, nullptr);
            }
            return;
        }
    }
}

void WindowsBackend::updateHub() {
    ComInit com;
    if (!com.ok()) {
        return;
    }

    ComPtr<IMMDeviceEnumerator> enumerator;
    if (FAILED(CoCreateInstance(CLSID_MMDeviceEnumerator, nullptr, CLSCTX_ALL, __uuidof(IMMDeviceEnumerator), reinterpret_cast<void**>(enumerator.GetAddressOf()))) || !enumerator) {
        return;
    }

    ComPtr<IMMDeviceCollection> collection;
    if (FAILED(enumerator->EnumAudioEndpoints(eRender, DEVICE_STATE_ACTIVE, collection.GetAddressOf())) || !collection) {
        return;
    }

    UINT count = 0;
    if (FAILED(collection->GetCount(&count))) {
        return;
    }

    std::wstring virtualDeviceId;
    for (UINT index = 0; index < count; ++index) {
        ComPtr<IMMDevice> device;
        if (FAILED(collection->Item(index, device.GetAddressOf())) || !device) {
            continue;
        }

        auto friendlyName = getFriendlyName(device);
        auto id = getDeviceId(device);
        if (!friendlyName.empty() && isVirtualHubDevice(wideToUtf8(friendlyName))) {
            if (previousDefaultDeviceId_.empty()) {
                ComPtr<IMMDevice> defaultDevice;
                if (SUCCEEDED(enumerator->GetDefaultAudioEndpoint(eRender, eMultimedia, defaultDevice.GetAddressOf())) && defaultDevice) {
                    previousDefaultDeviceId_ = wideToUtf8(getDeviceId(defaultDevice));
                }
            }
            virtualDeviceId = std::move(id);
            break;
        }
    }

    if (virtualDeviceId.empty()) {
        return;
    }

    auto policy = createPolicyConfig();
    if (!policy) {
        return;
    }

    policy->SetDefaultEndpoint(virtualDeviceId.c_str(), eConsole);
    policy->SetDefaultEndpoint(virtualDeviceId.c_str(), eMultimedia);
    policy->SetDefaultEndpoint(virtualDeviceId.c_str(), eCommunications);
}

void WindowsBackend::unloadHub() {
    if (previousDefaultDeviceId_.empty()) {
        return;
    }

    auto previousId = utf8ToWide(previousDefaultDeviceId_);
    auto policy = createPolicyConfig();
    if (!policy) {
        return;
    }

    policy->SetDefaultEndpoint(previousId.c_str(), eConsole);
    policy->SetDefaultEndpoint(previousId.c_str(), eMultimedia);
    policy->SetDefaultEndpoint(previousId.c_str(), eCommunications);
}

bool WindowsBackend::hasUsableHubDevice() {
    ComInit com;
    if (!com.ok()) {
        return false;
    }

    for (const auto& device : enumerateDevices()) {
        if (isVirtualHubDevice(wideToUtf8(device.friendlyName))) {
            return true;
        }
    }
    return false;
}

}  // namespace bridge

#else

namespace bridge {

WindowsBackend::WindowsBackend() = default;

std::vector<SinkInfo> WindowsBackend::listSinks() { return {}; }
void WindowsBackend::setVolume(const std::string&, int) {}
void WindowsBackend::updateHub() {}
void WindowsBackend::unloadHub() {}
bool WindowsBackend::hasUsableHubDevice() { return false; }
bool WindowsBackend::isEarbudDevice(const std::string&) const { return false; }
bool WindowsBackend::isVirtualHubDevice(const std::string&) const { return false; }

}  // namespace bridge

#endif
