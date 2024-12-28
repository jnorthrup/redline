cmake_minimum_required(VERSION 3.10)

# Function to configure LMStudio client for offline use
function(configure_lmstudio_offline)
    set(CONFIG_FILE ~/.local/cache/redline/lmstudio/config.json)
    set(OFFLINE_CONFIG "{\"offline\": true, \"cache_dir\": \"~/.local/cache/redline/lmstudio/cache\"}")

    if(NOT EXISTS ${CONFIG_FILE})
        file(WRITE ${CONFIG_FILE} ${OFFLINE_CONFIG})
    else()
        file(READ ${CONFIG_FILE} CURRENT_CONFIG)
        if(NOT CURRENT_CONFIG MATCHES "\"offline\": true")
            file(WRITE ${CONFIG_FILE} ${OFFLINE_CONFIG})
        endif()
    endif()
endfunction()

# Call the configure_lmstudio_offline function
configure_lmstudio_offline()
