from codingTools import *

def Yaz0Header(compressedYaz0File):
    magic = compressedYaz0File.read(4)
    if magic != b'Yaz0':
        raise ValueError(f"Invalid Yaz0 magic: {magic}")
    
    decompressedSize = BE_Unpack.uint(compressedYaz0File.read(4))
    reserved = compressedYaz0File.read(8)
    
    return decompressedSize

def Yaz0Decompress(compressedYaz0File, decompressedSize):
    decompressedData = bytearray()
    fileData = compressedYaz0File.read()
    pos = 0
    
    while len(decompressedData) < decompressedSize and pos < len(fileData):
        if pos >= len(fileData):
            break
        commandByte = fileData[pos]
        pos += 1
        
        for bit in range(8):
            if len(decompressedData) >= decompressedSize:
                break
            
            if pos >= len(fileData):
                break
                
            if (commandByte >> (7 - bit)) & 1:
                decompressedData.append(fileData[pos])
                pos += 1
            else:
                if pos + 1 >= len(fileData):
                    break
                    
                byte1 = fileData[pos]
                byte2 = fileData[pos + 1]
                pos += 2
                
                distance = ((byte1 & 0x0F) << 8) | byte2
                length = byte1 >> 4
                
                if length == 0:
                    if pos >= len(fileData):
                        break
                    length = fileData[pos] + 0x12
                    pos += 1
                else:
                    length += 2
                
                if distance >= len(decompressedData):
                    print(f"Warning: Invalid back-reference distance {distance} at position {len(decompressedData)}")
                    break
                
                startPos = len(decompressedData) - distance - 1
                actualLength = min(length, decompressedSize - len(decompressedData))

                for i in range(actualLength):
                    if startPos + i < 0 or startPos + i >= len(decompressedData):
                        print(f"Warning: Invalid copy position {startPos + i}")
                        break
                    decompressedData.append(decompressedData[startPos + i])
    
    return bytes(decompressedData[:decompressedSize])

def decompressYaz0(file):
    outName = fileTools.folder(file)+"/"+fileTools.nameNoExt(file)+".sarc"
    with open(file, "rb") as compressedYaz0File:
        decompressedSize = Yaz0Header(compressedYaz0File)
        decompressedData = Yaz0Decompress(compressedYaz0File, decompressedSize)
        
        with open(outName, "wb") as decompressedYaz0File:
            decompressedYaz0File.write(decompressedData)

        return outName #The SARC unpacker should use this name now
