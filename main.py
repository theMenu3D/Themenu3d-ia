
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import trimesh
import os
import uuid

app = FastAPI(title="TheMenu3D AI HyperRealistic Processor", version="2.0.0")

UPLOAD_DIR = "/tmp/themenu3d_storage"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/procesar-modelo-3d/")
async def procesar_modelo(file: UploadFile = File(...)):
    try:
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ["glb", "gltf", "obj"]:
            raise HTTPException(status_code=400, detail="Formato no compatible. Usa GLB, GLTF u OBJ.")

        input_filename = f"{uuid.uuid4()}_{file.filename}"
        input_path = os.path.join(UPLOAD_DIR, input_filename)
        
        contents = await file.read()
        with open(input_path, "wb") as f:
            f.write(contents)

        scene_or_mesh = trimesh.load(input_path, force='scene')

        if isinstance(scene_or_mesh, trimesh.Scene):
            scene = scene_or_mesh
            extents = scene.extents
            max_dim = max(extents) if extents is not None and len(extents) > 0 else 0
            if max_dim > 0:
                target_size = 0.28
                scale_factor = target_size / max_dim
                scene.apply_scale(scale_factor)
            
            output_filename = f"hyperrealistic_{uuid.uuid4()}.glb"
            output_path = os.path.join(UPLOAD_DIR, output_filename)
            scene.export(output_path, file_type='glb')
        else:
            mesh = scene_or_mesh
            if not isinstance(mesh, trimesh.Trimesh):
                raise HTTPException(status_code=400, detail="No se pudo extraer una estructura 3D válida.")

            extents = mesh.extents
            max_dim = max(extents)
            if max_dim > 0:
                target_size = 0.28
                scale_factor = target_size / max_dim
                mesh.apply_scale(scale_factor)

            output_filename = f"hyperrealistic_{uuid.uuid4()}.glb"
            output_path = os.path.join(UPLOAD_DIR, output_filename)
            mesh.export(output_path, file_type='glb')

        return FileResponse(
            output_path, 
            media_type="model/gltf-binary", 
            filename="plato_hiperrealista.glb"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno procesando el hiperrealismo: {str(e)}")

@app.get("/")
def read_root():
    return {"status": "online", "service": "TheMenu3D AI HyperRealistic Processor active"}
