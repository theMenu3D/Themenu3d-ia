from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import uuid

app = FastAPI(title="TheMenu3D Color-Safe Pipeline", version="2.2.0")

UPLOAD_DIR = "/tmp/themenu3d_storage"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/procesar-modelo-3d/")
async def procesar_modelo(file: UploadFile = File(...)):
    try:
        ext = (file.filename.split(".")[-1].lower() if file.filename else "")
        if ext not in ["glb", "gltf"]:
            raise HTTPException(status_code=400, detail="Formato no compatible. Solo GLB/GLTF texturizado.")

        contents = await file.read()
        
        # Validación anti-blanco / archivo vacío en origen (< 50KB suele ser geometría sin textura/roto)
        if len(contents) < 50000:
            raise HTTPException(
                status_code=422, 
                detail="Error de hiperrealismo: el archivo de origen pesa muy poco o carece de texturas de color."
            )

        output_filename = f"native_color_{uuid.uuid4()}.glb"
        output_path = os.path.join(UPLOAD_DIR, output_filename)
        
        with open(output_path, "wb") as f:
            f.write(contents)

        # BYPASS TOTAL: Devuelve el binario exacto del proveedor con 100% color original.
        # La escala física (28 cm platos / 10 cm bebidas) se aplica en el visor Three.js (model.scale.set).
        return FileResponse(
            output_path,
            media_type="model/gltf-binary",
            filename="plato_color_original.glb"
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en pipeline de color: {str(e)}")

@app.get("/")
def read_root():
    return {"status": "online", "service": "TheMenu3D Color-Safe Pipeline"}
