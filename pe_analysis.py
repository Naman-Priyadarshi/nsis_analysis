import pefile

def analyze_pe(exe_path):
    try:
        pe = pefile.PE(exe_path)

        pe_info = {
            "Entry Point": hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint),
            "Image Base": hex(pe.OPTIONAL_HEADER.ImageBase),
            "Timestamp": pe.FILE_HEADER.TimeDateStamp,
            "Number of Sections": pe.FILE_HEADER.NumberOfSections,
            "Section Names": [s.Name.decode().strip('\x00') for s in pe.sections],
        }

        # Check for overlay (common in NSIS installers)
        overlay_offset = pe.get_overlay_data_start_offset()
        if overlay_offset:
            pe_info["Overlay Present"] = True
            pe_info["Overlay Offset"] = overlay_offset
        else:
            pe_info["Overlay Present"] = False

        return pe_info

    except Exception as e:
        return {"error": f"PE analysis failed: {str(e)}"}
