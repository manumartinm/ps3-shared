from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Estados posibles de una tarea"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskBase(BaseModel):
    """Modelo base para las tareas"""
    filename: str = Field(..., description="Nombre del archivo PDF original")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Estado actual de la tarea")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")
    updated_at: datetime = Field(default_factory=datetime.now, description="Fecha de última actualización")


class TaskCreate(TaskBase):
    """Modelo para crear una nueva tarea"""
    pass


class Task(TaskBase):
    """Modelo completo de una tarea"""
    id: str = Field(..., description="ID único de la tarea")
    minio_path: Optional[str] = Field(None, description="Ruta del archivo en MinIO")
    parquet_path: Optional[str] = Field(None, description="Ruta del archivo parquet en MinIO")
    error_message: Optional[str] = Field(None, description="Mensaje de error si la tarea falló")
    processing_started_at: Optional[datetime] = Field(None, description="Cuándo comenzó el procesamiento")
    completed_at: Optional[datetime] = Field(None, description="Cuándo se completó la tarea")


class TaskResponse(BaseModel):
    """Modelo de respuesta para las tareas"""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo de la operación")
    data: Optional[Task] = Field(None, description="Datos de la tarea si la operación fue exitosa")
    error: Optional[str] = Field(None, description="Detalle del error si la operación falló")


class TaskListResponse(BaseModel):
    """Modelo de respuesta para listar tareas"""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo de la operación")
    data: list[Task] = Field(default_factory=list, description="Lista de tareas")
    total: int = Field(..., description="Total de tareas encontradas") 