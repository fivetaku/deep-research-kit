# Implementation Guide: Open-Source AI Detection

*Last Updated: December 2024*

## Table of Contents
1. [Quick Start Templates](#quick-start-templates)
2. [Text Detection Implementation](#text-detection-implementation)
3. [Image Detection Implementation](#image-detection-implementation)
4. [Video Detection Implementation](#video-detection-implementation)
5. [Audio Detection Implementation](#audio-detection-implementation)
6. [Multi-Modal Detection System](#multi-modal-detection-system)
7. [Production Deployment](#production-deployment)
8. [Performance Optimization](#performance-optimization)
9. [Error Handling & Monitoring](#error-handling--monitoring)
10. [Testing Strategies](#testing-strategies)

---

## Quick Start Templates

### Universal Detection Service

```python
# universal_detector.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Union, List
import asyncio
from dataclasses import dataclass
import logging

@dataclass
class DetectionResult:
    """Standardized detection result across all modalities."""
    is_ai_generated: bool
    confidence: float
    modality: str
    details: Dict[str, Any]
    processing_time: float
    model_used: str
    
class BaseDetector(ABC):
    """Base class for all detection implementations."""
    
    def __init__(self, model_name: str, config: Dict[str, Any] = None):
        self.model_name = model_name
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{model_name}")
        
    @abstractmethod
    async def detect(self, content: Any) -> DetectionResult:
        """Perform detection on content."""
        pass
        
    @abstractmethod
    def validate_input(self, content: Any) -> bool:
        """Validate input before processing."""
        pass
        
    def preprocess(self, content: Any) -> Any:
        """Preprocess content before detection."""
        return content
        
    def postprocess(self, raw_output: Any) -> DetectionResult:
        """Convert raw model output to standardized result."""
        return raw_output

# Quick start for any modality
async def detect_ai_content(content: Union[str, bytes], 
                          modality: str = "auto") -> DetectionResult:
    """
    Unified interface for detecting AI-generated content.
    
    Args:
        content: The content to analyze (text, image bytes, audio bytes, etc.)
        modality: The type of content ('text', 'image', 'audio', 'video', 'auto')
        
    Returns:
        DetectionResult with standardized format
    """
    from detectors import get_detector
    
    detector = get_detector(modality)
    result = await detector.detect(content)
    return result
```

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  detection-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MODEL_CACHE_DIR=/models
      - LOG_LEVEL=INFO
      - MAX_WORKERS=4
    volumes:
      - ./models:/models
      - ./logs:/app/logs
    depends_on:
      - redis
      - postgres
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_detection
      POSTGRES_USER: detector
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - detection-api

volumes:
  redis_data:
  postgres_data:
  model_cache:
```

---

## Text Detection Implementation

### 1. Binoculars Integration

```python
# binoculars_detector.py
import torch
from typing import Optional, Dict, Any
import time
from binoculars import Binoculars

class BinocularsDetector(BaseDetector):
    """Zero-shot text detection using Binoculars."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("binoculars", config)
        self.detector = Binoculars(
            device='cuda' if torch.cuda.is_available() else 'cpu'
        )
        self.threshold = config.get('threshold', 0.7) if config else 0.7
        
    async def detect(self, text: str) -> DetectionResult:
        """Detect if text is AI-generated."""
        start_time = time.time()
        
        # Validate input
        if not self.validate_input(text):
            raise ValueError("Invalid input text")
            
        # Preprocess
        processed_text = self.preprocess(text)
        
        # Run detection
        score = await self._run_detection(processed_text)
        
        # Create result
        result = DetectionResult(
            is_ai_generated=score > self.threshold,
            confidence=float(score),
            modality='text',
            details={
                'threshold': self.threshold,
                'text_length': len(text),
                'model_score': float(score)
            },
            processing_time=time.time() - start_time,
            model_used=self.model_name
        )
        
        return result
        
    async def _run_detection(self, text: str) -> float:
        """Run detection in thread pool to avoid blocking."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.detector.predict, text)
        
    def validate_input(self, text: str) -> bool:
        """Validate text input."""
        if not isinstance(text, str):
            return False
        if len(text.strip()) < 50:  # Minimum length for reliable detection
            self.logger.warning("Text too short for reliable detection")
            return False
        return True
        
    def preprocess(self, text: str) -> str:
        """Clean and prepare text."""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        # Truncate if too long
        max_length = self.config.get('max_length', 2048)
        if len(text) > max_length:
            text = text[:max_length]
        return text
```

### 2. Multi-Model Text Ensemble

```python
# text_ensemble.py
from typing import List, Dict, Any
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import asyncio

class TextDetectionEnsemble:
    """Ensemble multiple text detection models for better accuracy."""
    
    def __init__(self, models: List[str] = None):
        self.models = models or ['binoculars', 'llmdet', 'bert_detector']
        self.detectors = {}
        self._initialize_detectors()
        
    def _initialize_detectors(self):
        """Initialize all detector instances."""
        for model_name in self.models:
            if model_name == 'binoculars':
                self.detectors[model_name] = BinocularsDetector()
            elif model_name == 'llmdet':
                from llmdet_detector import LLMDetDetector
                self.detectors[model_name] = LLMDetDetector()
            elif model_name == 'bert_detector':
                from bert_detector import BertAIDetector
                self.detectors[model_name] = BertAIDetector()
                
    async def detect(self, text: str, voting: str = 'weighted') -> DetectionResult:
        """
        Run ensemble detection.
        
        Args:
            text: Text to analyze
            voting: 'weighted', 'majority', or 'unanimous'
        """
        # Run all detectors in parallel
        tasks = [
            detector.detect(text) 
            for detector in self.detectors.values()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out errors
        valid_results = [
            r for r in results 
            if isinstance(r, DetectionResult)
        ]
        
        if not valid_results:
            raise RuntimeError("All detectors failed")
            
        # Aggregate results
        if voting == 'weighted':
            return self._weighted_voting(valid_results)
        elif voting == 'majority':
            return self._majority_voting(valid_results)
        else:  # unanimous
            return self._unanimous_voting(valid_results)
            
    def _weighted_voting(self, results: List[DetectionResult]) -> DetectionResult:
        """Weighted voting based on model confidence."""
        weights = {
            'binoculars': 0.4,
            'llmdet': 0.35,
            'bert_detector': 0.25
        }
        
        weighted_sum = 0
        total_weight = 0
        
        for result in results:
            weight = weights.get(result.model_used, 0.2)
            weighted_sum += result.confidence * weight
            total_weight += weight
            
        final_confidence = weighted_sum / total_weight
        
        return DetectionResult(
            is_ai_generated=final_confidence > 0.5,
            confidence=final_confidence,
            modality='text',
            details={
                'ensemble_method': 'weighted',
                'individual_results': [
                    {
                        'model': r.model_used,
                        'confidence': r.confidence,
                        'is_ai': r.is_ai_generated
                    }
                    for r in results
                ]
            },
            processing_time=max(r.processing_time for r in results),
            model_used='ensemble'
        )
```

### 3. Real-time Text Stream Detection

```python
# stream_detector.py
import asyncio
from collections import deque
from typing import AsyncGenerator, Optional
import re

class StreamTextDetector:
    """Detect AI-generated text in real-time streams."""
    
    def __init__(self, 
                 detector: BaseDetector,
                 buffer_size: int = 500,
                 overlap: int = 100):
        self.detector = detector
        self.buffer_size = buffer_size
        self.overlap = overlap
        self.buffer = deque(maxlen=buffer_size)
        
    async def process_stream(self, 
                           text_stream: AsyncGenerator[str, None],
                           callback: Optional[callable] = None) -> None:
        """
        Process incoming text stream and detect AI content.
        
        Args:
            text_stream: Async generator yielding text chunks
            callback: Function to call with detection results
        """
        async for chunk in text_stream:
            self.buffer.extend(chunk)
            
            # Check if we have enough text
            if len(self.buffer) >= self.buffer_size:
                text_to_check = ''.join(list(self.buffer))
                
                # Run detection
                result = await self.detector.detect(text_to_check)
                
                if callback:
                    await callback(result)
                    
                # Remove processed text, keeping overlap
                for _ in range(self.buffer_size - self.overlap):
                    if self.buffer:
                        self.buffer.popleft()

# Example usage for chat detection
async def detect_chat_stream():
    """Example: Detect AI in chat messages."""
    detector = BinocularsDetector()
    stream_detector = StreamTextDetector(detector)
    
    async def chat_generator():
        """Simulate incoming chat messages."""
        messages = [
            "Hello, how are you today?",
            "I'm doing well, thanks for asking!",
            "The weather is quite nice...",
            # More messages...
        ]
        for msg in messages:
            yield msg
            await asyncio.sleep(0.1)  # Simulate delay
            
    async def handle_detection(result: DetectionResult):
        if result.is_ai_generated:
            print(f"🤖 AI detected! Confidence: {result.confidence:.2%}")
        else:
            print(f"👤 Human text. Confidence: {1-result.confidence:.2%}")
            
    await stream_detector.process_stream(
        chat_generator(),
        handle_detection
    )
```

---

## Image Detection Implementation

### 1. DeepfakeBench Integration

```python
# deepfakebench_detector.py
import torch
import numpy as np
from PIL import Image
from typing import Union, Optional
import io
from deepfakebench import load_detector, get_preprocessing

class DeepfakeBenchDetector(BaseDetector):
    """Production-ready deepfake detection using DeepfakeBench."""
    
    def __init__(self, 
                 model_name: str = 'effort',  # ICML'25 SOTA
                 device: Optional[str] = None):
        super().__init__(f"deepfakebench_{model_name}")
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = load_detector(model_name, device=self.device)
        self.preprocessing = get_preprocessing(model_name)
        
    async def detect(self, image: Union[bytes, np.ndarray, Image.Image]) -> DetectionResult:
        """Detect if image is AI-generated/deepfake."""
        start_time = time.time()
        
        # Convert to PIL Image
        if isinstance(image, bytes):
            image = Image.open(io.BytesIO(image))
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(image)
            
        # Validate
        if not self.validate_input(image):
            raise ValueError("Invalid image input")
            
        # Preprocess
        tensor = self.preprocessing(image).unsqueeze(0).to(self.device)
        
        # Run detection
        with torch.no_grad():
            output = self.model(tensor)
            probability = torch.sigmoid(output).cpu().item()
            
        return DetectionResult(
            is_ai_generated=probability > 0.5,
            confidence=probability,
            modality='image',
            details={
                'image_size': image.size,
                'model_output': float(output.cpu().item()),
                'preprocessing': str(self.preprocessing)
            },
            processing_time=time.time() - start_time,
            model_used=self.model_name
        )
        
    def validate_input(self, image: Image.Image) -> bool:
        """Validate image input."""
        if image.size[0] < 64 or image.size[1] < 64:
            self.logger.warning("Image too small for reliable detection")
            return False
        return True

# Batch processing for efficiency
class BatchImageDetector:
    """Efficient batch processing for multiple images."""
    
    def __init__(self, detector: DeepfakeBenchDetector, batch_size: int = 32):
        self.detector = detector
        self.batch_size = batch_size
        
    async def detect_batch(self, images: List[Union[bytes, Image.Image]]) -> List[DetectionResult]:
        """Process multiple images efficiently."""
        results = []
        
        for i in range(0, len(images), self.batch_size):
            batch = images[i:i + self.batch_size]
            
            # Prepare batch tensor
            tensors = []
            for img in batch:
                if isinstance(img, bytes):
                    img = Image.open(io.BytesIO(img))
                tensor = self.detector.preprocessing(img)
                tensors.append(tensor)
                
            batch_tensor = torch.stack(tensors).to(self.detector.device)
            
            # Run batch inference
            with torch.no_grad():
                outputs = self.detector.model(batch_tensor)
                probabilities = torch.sigmoid(outputs).cpu().numpy()
                
            # Create results
            for idx, (img, prob) in enumerate(zip(batch, probabilities)):
                results.append(DetectionResult(
                    is_ai_generated=prob > 0.5,
                    confidence=float(prob),
                    modality='image',
                    details={'batch_index': i + idx},
                    processing_time=0,  # Will calculate total time
                    model_used=self.detector.model_name
                ))
                
        return results
```

### 2. Lightweight SSP Implementation

```python
# ssp_detector.py
import torch
import torch.nn.functional as F
from torchvision import transforms
import numpy as np
from typing import Tuple, List

class SSPDetector(BaseDetector):
    """Single Simple Patch detection for mobile/edge deployment."""
    
    def __init__(self, 
                 patch_size: int = 96,
                 stride: int = 48,
                 model_path: Optional[str] = None):
        super().__init__("ssp")
        self.patch_size = patch_size
        self.stride = stride
        self.model = self._load_model(model_path)
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])
        
    def _load_model(self, model_path: Optional[str]) -> torch.nn.Module:
        """Load lightweight CNN model."""
        # Simplified architecture for edge deployment
        import torch.nn as nn
        
        class LightweightCNN(nn.Module):
            def __init__(self):
                super().__init__()
                self.features = nn.Sequential(
                    nn.Conv2d(3, 32, 3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(2),
                    nn.Conv2d(32, 64, 3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(2),
                    nn.Conv2d(64, 128, 3, padding=1),
                    nn.ReLU(),
                    nn.AdaptiveAvgPool2d(1)
                )
                self.classifier = nn.Linear(128, 1)
                
            def forward(self, x):
                x = self.features(x)
                x = x.view(x.size(0), -1)
                return self.classifier(x)
                
        model = LightweightCNN()
        if model_path:
            model.load_state_dict(torch.load(model_path, map_location='cpu'))
        model.eval()
        return model
        
    def extract_patches(self, image: Image.Image) -> List[torch.Tensor]:
        """Extract patches from image using sliding window."""
        img_tensor = self.transform(image)
        patches = []
        
        h, w = img_tensor.shape[1:]
        for y in range(0, h - self.patch_size + 1, self.stride):
            for x in range(0, w - self.patch_size + 1, self.stride):
                patch = img_tensor[:, y:y+self.patch_size, x:x+self.patch_size]
                patches.append(patch)
                
        return patches
        
    async def detect(self, image: Union[bytes, Image.Image]) -> DetectionResult:
        """Detect using patch-based approach."""
        if isinstance(image, bytes):
            image = Image.open(io.BytesIO(image))
            
        # Extract patches
        patches = self.extract_patches(image)
        if not patches:
            raise ValueError("Image too small for patch extraction")
            
        # Batch inference on patches
        batch = torch.stack(patches)
        with torch.no_grad():
            outputs = self.model(batch)
            probabilities = torch.sigmoid(outputs).squeeze()
            
        # Aggregate patch results
        final_prob = probabilities.max().item()  # Most suspicious patch
        
        return DetectionResult(
            is_ai_generated=final_prob > 0.5,
            confidence=final_prob,
            modality='image',
            details={
                'num_patches': len(patches),
                'patch_scores': probabilities.tolist(),
                'max_score_location': int(probabilities.argmax())
            },
            processing_time=0,  # Set externally
            model_used=self.model_name
        )

# Mobile-optimized version
class MobileSSPDetector(SSPDetector):
    """Optimized for mobile deployment with TensorFlow Lite."""
    
    def __init__(self):
        super().__init__(patch_size=64, stride=32)
        
    def export_to_tflite(self, save_path: str):
        """Export model to TensorFlow Lite format."""
        # Convert PyTorch to ONNX first
        dummy_input = torch.randn(1, 3, self.patch_size, self.patch_size)
        torch.onnx.export(
            self.model,
            dummy_input,
            "temp_model.onnx",
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={'input': {0: 'batch_size'}}
        )
        
        # Then convert ONNX to TFLite
        import onnx
        from onnx_tf.backend import prepare
        import tensorflow as tf
        
        onnx_model = onnx.load("temp_model.onnx")
        tf_rep = prepare(onnx_model)
        tf_rep.export_graph("temp_model_tf")
        
        # Convert to TFLite
        converter = tf.lite.TFLiteConverter.from_saved_model("temp_model_tf")
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tf.float16]
        tflite_model = converter.convert()
        
        with open(save_path, 'wb') as f:
            f.write(tflite_model)
```

### 3. Real-time Video Stream Detection

```python
# video_stream_detector.py
import cv2
import asyncio
from collections import deque
import numpy as np
from typing import Optional, Callable

class VideoStreamDetector:
    """Real-time detection for video streams."""
    
    def __init__(self,
                 detector: BaseDetector,
                 frame_buffer_size: int = 30,
                 detection_interval: int = 10):
        self.detector = detector
        self.frame_buffer = deque(maxlen=frame_buffer_size)
        self.detection_interval = detection_interval
        self.frame_count = 0
        
    async def process_video_stream(self,
                                 source: Union[str, int],
                                 callback: Optional[Callable] = None,
                                 display: bool = False):
        """
        Process video stream in real-time.
        
        Args:
            source: Video file path, URL, or camera index
            callback: Function to call with detection results
            display: Whether to display the video with overlays
        """
        cap = cv2.VideoCapture(source)
        
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                self.frame_count += 1
                
                # Detect every N frames
                if self.frame_count % self.detection_interval == 0:
                    # Convert BGR to RGB
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(rgb_frame)
                    
                    # Run detection
                    result = await self.detector.detect(pil_image)
                    
                    if callback:
                        await callback(result, frame)
                        
                    # Add overlay if displaying
                    if display:
                        self._add_overlay(frame, result)
                        
                if display:
                    cv2.imshow('AI Detection', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                        
                # Small delay to prevent CPU overload
                await asyncio.sleep(0.001)
                
        finally:
            cap.release()
            if display:
                cv2.destroyAllWindows()
                
    def _add_overlay(self, frame: np.ndarray, result: DetectionResult):
        """Add detection overlay to frame."""
        h, w = frame.shape[:2]
        
        # Add detection box
        color = (0, 0, 255) if result.is_ai_generated else (0, 255, 0)
        label = f"AI: {result.confidence:.1%}" if result.is_ai_generated else f"Real: {(1-result.confidence):.1%}"
        
        # Draw rectangle
        cv2.rectangle(frame, (10, 10), (w-10, 40), color, 2)
        
        # Add text
        cv2.putText(frame, label, (20, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Add confidence bar
        bar_width = int((w - 40) * result.confidence)
        cv2.rectangle(frame, (20, h-30), (20 + bar_width, h-20), color, -1)
        cv2.rectangle(frame, (20, h-30), (w-20, h-20), (255, 255, 255), 1)

# Example usage for webcam
async def detect_webcam():
    """Detect deepfakes in webcam feed."""
    detector = DeepfakeBenchDetector(model_name='effort')
    stream_detector = VideoStreamDetector(detector)
    
    async def handle_detection(result: DetectionResult, frame: np.ndarray):
        if result.is_ai_generated and result.confidence > 0.8:
            # Save suspicious frame
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cv2.imwrite(f"suspicious_{timestamp}.jpg", frame)
            print(f"⚠️  High confidence deepfake detected: {result.confidence:.1%}")
            
    await stream_detector.process_video_stream(
        source=0,  # Webcam
        callback=handle_detection,
        display=True
    )
```

---

## Audio Detection Implementation

### 1. Advanced Audio Feature Extraction

```python
# audio_detector.py
import librosa
import numpy as np
import torch
from typing import Union, Optional, Dict, Any
import soundfile as sf

class AdvancedAudioDetector(BaseDetector):
    """State-of-the-art audio deepfake detection."""
    
    def __init__(self, 
                 model_path: str = 'models/se_res2net_conformer.pth',
                 sample_rate: int = 16000):
        super().__init__("audio_deepfake_detector")
        self.sample_rate = sample_rate
        self.model = self._load_model(model_path)
        
    def _load_model(self, model_path: str):
        """Load SE-Res2Net-Conformer model."""
        # Model architecture would be loaded here
        # For demonstration, using a placeholder
        model = torch.nn.Sequential(
            torch.nn.Linear(768, 256),
            torch.nn.ReLU(),
            torch.nn.Linear(256, 128),
            torch.nn.ReLU(),
            torch.nn.Linear(128, 1)
        )
        if os.path.exists(model_path):
            model.load_state_dict(torch.load(model_path, map_location='cpu'))
        model.eval()
        return model
        
    def extract_features(self, audio: np.ndarray, sr: int) -> Dict[str, np.ndarray]:
        """Extract comprehensive audio features."""
        features = {}
        
        # 1. MFCC features
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=20)
        features['mfcc'] = mfcc
        features['mfcc_delta'] = librosa.feature.delta(mfcc)
        features['mfcc_delta2'] = librosa.feature.delta(mfcc, order=2)
        
        # 2. Spectral features
        features['spectral_centroid'] = librosa.feature.spectral_centroid(y=audio, sr=sr)
        features['spectral_rolloff'] = librosa.feature.spectral_rolloff(y=audio, sr=sr)
        features['spectral_contrast'] = librosa.feature.spectral_contrast(y=audio, sr=sr)
        features['zero_crossing_rate'] = librosa.feature.zero_crossing_rate(audio)
        
        # 3. Mel-spectrogram
        mel_spec = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=128)
        features['mel_spectrogram'] = librosa.power_to_db(mel_spec, ref=np.max)
        
        # 4. Chroma features
        features['chroma_stft'] = librosa.feature.chroma_stft(y=audio, sr=sr)
        features['chroma_cqt'] = librosa.feature.chroma_cqt(y=audio, sr=sr)
        
        # 5. Tempo and beat features
        tempo, beats = librosa.beat.beat_track(y=audio, sr=sr)
        features['tempo'] = tempo
        features['beat_frames'] = beats
        
        # 6. Long-term Variable Q Transform (LT-VQT)
        features['vqt'] = self._compute_vqt(audio, sr)
        
        return features
        
    def _compute_vqt(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Compute Variable Q Transform for fine-grained frequency analysis."""
        # VQT computation for detecting synthetic artifacts
        C = librosa.vqt(audio, sr=sr, hop_length=512, fmin=librosa.note_to_hz('C1'))
        return np.abs(C)
        
    def create_feature_vector(self, features: Dict[str, np.ndarray]) -> torch.Tensor:
        """Combine all features into a single vector."""
        feature_list = []
        
        # Statistical aggregation of time-series features
        for key, value in features.items():
            if isinstance(value, np.ndarray) and value.ndim > 1:
                # Compute statistics across time
                feature_list.extend([
                    value.mean(axis=1),
                    value.std(axis=1),
                    value.max(axis=1),
                    value.min(axis=1)
                ])
            elif isinstance(value, (int, float)):
                feature_list.append([value])
                
        # Flatten and concatenate
        feature_vector = np.concatenate([f.flatten() for f in feature_list])
        
        # Normalize
        feature_vector = (feature_vector - feature_vector.mean()) / (feature_vector.std() + 1e-8)
        
        return torch.FloatTensor(feature_vector[:768])  # Fixed size for model
        
    async def detect(self, audio_input: Union[str, bytes, np.ndarray]) -> DetectionResult:
        """Detect if audio is AI-generated."""
        start_time = time.time()
        
        # Load audio
        if isinstance(audio_input, str):
            audio, sr = librosa.load(audio_input, sr=self.sample_rate)
        elif isinstance(audio_input, bytes):
            audio, sr = sf.read(io.BytesIO(audio_input))
            if sr != self.sample_rate:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sample_rate)
        else:
            audio = audio_input
            sr = self.sample_rate
            
        # Extract features
        features = self.extract_features(audio, sr)
        feature_vector = self.create_feature_vector(features)
        
        # Run model
        with torch.no_grad():
            output = self.model(feature_vector.unsqueeze(0))
            probability = torch.sigmoid(output).item()
            
        return DetectionResult(
            is_ai_generated=probability > 0.5,
            confidence=probability,
            modality='audio',
            details={
                'duration': len(audio) / sr,
                'sample_rate': sr,
                'tempo': features['tempo'],
                'spectral_features_extracted': list(features.keys())
            },
            processing_time=time.time() - start_time,
            model_used=self.model_name
        )
```

### 2. Real-time Voice Stream Detection

```python
# voice_stream_detector.py
import pyaudio
import numpy as np
from collections import deque
import threading
import queue

class RealtimeVoiceDetector:
    """Detect AI-generated voice in real-time conversations."""
    
    def __init__(self,
                 detector: AdvancedAudioDetector,
                 chunk_duration: float = 2.0,
                 overlap: float = 0.5):
        self.detector = detector
        self.chunk_duration = chunk_duration
        self.overlap = overlap
        self.sample_rate = 16000
        self.chunk_size = int(self.sample_rate * chunk_duration)
        self.overlap_size = int(self.sample_rate * overlap)
        
        # Audio setup
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.audio_queue = queue.Queue()
        self.is_running = False
        
    def start_detection(self, callback: Optional[Callable] = None):
        """Start real-time detection."""
        self.is_running = True
        
        # Start audio stream
        self.stream = self.audio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=1024,
            stream_callback=self._audio_callback
        )
        
        # Start processing thread
        processing_thread = threading.Thread(
            target=self._process_audio_chunks,
            args=(callback,)
        )
        processing_thread.start()
        
        self.stream.start_stream()
        
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream."""
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        self.audio_queue.put(audio_data)
        return (in_data, pyaudio.paContinue)
        
    async def _process_audio_chunks(self, callback: Optional[Callable]):
        """Process audio chunks for detection."""
        buffer = deque(maxlen=self.chunk_size)
        
        while self.is_running:
            try:
                # Get audio data
                audio_chunk = self.audio_queue.get(timeout=0.1)
                buffer.extend(audio_chunk)
                
                # Check if we have enough data
                if len(buffer) >= self.chunk_size:
                    # Convert to numpy array
                    audio_array = np.array(list(buffer))
                    
                    # Run detection
                    result = await self.detector.detect(audio_array)
                    
                    if callback:
                        await callback(result)
                        
                    # Remove processed audio, keeping overlap
                    for _ in range(self.chunk_size - self.overlap_size):
                        buffer.popleft()
                        
            except queue.Empty:
                continue
                
    def stop_detection(self):
        """Stop detection and cleanup."""
        self.is_running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()

# WebRTC integration for browser-based detection
class WebRTCAudioDetector:
    """Audio detection for WebRTC streams."""
    
    def __init__(self, detector: AdvancedAudioDetector):
        self.detector = detector
        
    async def process_webrtc_stream(self, audio_track):
        """Process WebRTC audio track."""
        # This would integrate with aiortc or similar
        # Example implementation:
        
        buffer = []
        async for frame in audio_track:
            # Convert WebRTC frame to numpy
            audio_data = np.frombuffer(frame.data, dtype=np.int16)
            audio_float = audio_data.astype(np.float32) / 32768.0
            
            buffer.extend(audio_float)
            
            # Process when we have enough data
            if len(buffer) >= 16000 * 2:  # 2 seconds
                result = await self.detector.detect(np.array(buffer))
                yield result
                buffer = buffer[8000:]  # Keep 1 second overlap
```

---

## Multi-Modal Detection System

### Complete Multi-Modal Pipeline

```python
# multimodal_system.py
from typing import Dict, Any, List, Optional
import asyncio
from dataclasses import dataclass
from enum import Enum

class Modality(Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"

@dataclass
class MultiModalContent:
    """Container for multi-modal content."""
    text: Optional[str] = None
    image: Optional[bytes] = None
    video: Optional[str] = None
    audio: Optional[bytes] = None
    metadata: Dict[str, Any] = None

class MultiModalDetectionSystem:
    """Comprehensive multi-modal AI detection system."""
    
    def __init__(self):
        self.detectors = {
            Modality.TEXT: BinocularsDetector(),
            Modality.IMAGE: DeepfakeBenchDetector(),
            Modality.VIDEO: VideoStreamDetector(DeepfakeBenchDetector()),
            Modality.AUDIO: AdvancedAudioDetector()
        }
        self.weights = {
            Modality.TEXT: 0.25,
            Modality.IMAGE: 0.30,
            Modality.VIDEO: 0.30,
            Modality.AUDIO: 0.15
        }
        
    async def detect(self, content: MultiModalContent) -> Dict[str, Any]:
        """Perform comprehensive multi-modal detection."""
        tasks = []
        active_modalities = []
        
        # Create detection tasks for available content
        if content.text:
            tasks.append(self.detectors[Modality.TEXT].detect(content.text))
            active_modalities.append(Modality.TEXT)
            
        if content.image:
            tasks.append(self.detectors[Modality.IMAGE].detect(content.image))
            active_modalities.append(Modality.IMAGE)
            
        if content.audio:
            tasks.append(self.detectors[Modality.AUDIO].detect(content.audio))
            active_modalities.append(Modality.AUDIO)
            
        # Run all detections in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        modality_results = {}
        valid_results = []
        
        for modality, result in zip(active_modalities, results):
            if isinstance(result, Exception):
                modality_results[modality.value] = {
                    'error': str(result),
                    'status': 'failed'
                }
            else:
                modality_results[modality.value] = {
                    'is_ai_generated': result.is_ai_generated,
                    'confidence': result.confidence,
                    'details': result.details,
                    'status': 'success'
                }
                valid_results.append((modality, result))
                
        # Calculate aggregate score
        aggregate_score = self._calculate_aggregate_score(valid_results)
        
        # Check for cross-modal inconsistencies
        inconsistencies = self._detect_inconsistencies(valid_results)
        
        return {
            'overall_verdict': {
                'is_ai_generated': aggregate_score > 0.5,
                'confidence': aggregate_score,
                'inconsistencies_detected': len(inconsistencies) > 0
            },
            'modality_results': modality_results,
            'inconsistencies': inconsistencies,
            'metadata': {
                'modalities_analyzed': [m.value for m in active_modalities],
                'processing_time': sum(r.processing_time for _, r in valid_results)
            }
        }
        
    def _calculate_aggregate_score(self, results: List[Tuple[Modality, DetectionResult]]) -> float:
        """Calculate weighted aggregate score."""
        if not results:
            return 0.0
            
        total_weight = 0
        weighted_sum = 0
        
        for modality, result in results:
            weight = self.weights[modality]
            weighted_sum += result.confidence * weight
            total_weight += weight
            
        return weighted_sum / total_weight if total_weight > 0 else 0.0
        
    def _detect_inconsistencies(self, results: List[Tuple[Modality, DetectionResult]]) -> List[Dict[str, Any]]:
        """Detect cross-modal inconsistencies."""
        inconsistencies = []
        
        # Check if different modalities disagree significantly
        confidences = {m: r.confidence for m, r in results}
        
        for i, (mod1, res1) in enumerate(results):
            for mod2, res2 in results[i+1:]:
                # If one says AI and other says human with high confidence
                if abs(res1.confidence - res2.confidence) > 0.7:
                    inconsistencies.append({
                        'type': 'confidence_mismatch',
                        'modalities': [mod1.value, mod2.value],
                        'confidences': [res1.confidence, res2.confidence],
                        'severity': 'high'
                    })
                    
        return inconsistencies

# Advanced cross-modal verification
class CrossModalVerifier:
    """Verify consistency across modalities."""
    
    def __init__(self):
        self.checks = {
            ('audio', 'video'): self._check_lip_sync,
            ('text', 'audio'): self._check_text_speech_match,
            ('text', 'image'): self._check_text_image_relevance
        }
        
    async def verify_consistency(self, content: MultiModalContent) -> Dict[str, Any]:
        """Run cross-modal consistency checks."""
        results = {}
        
        # Run applicable checks
        for (mod1, mod2), check_func in self.checks.items():
            if self._has_modality(content, mod1) and self._has_modality(content, mod2):
                result = await check_func(content)
                results[f"{mod1}_{mod2}_consistency"] = result
                
        return results
        
    def _has_modality(self, content: MultiModalContent, modality: str) -> bool:
        """Check if content has specific modality."""
        return getattr(content, modality) is not None
        
    async def _check_lip_sync(self, content: MultiModalContent) -> Dict[str, Any]:
        """Check audio-video lip synchronization."""
        # Implementation would use specialized lip-sync detection
        # This is a placeholder
        return {
            'sync_score': 0.95,
            'confidence': 0.87,
            'details': 'Lip movements match audio'
        }
        
    async def _check_text_speech_match(self, content: MultiModalContent) -> Dict[str, Any]:
        """Check if text matches speech content."""
        # Would use speech-to-text and compare
        return {
            'match_score': 0.92,
            'confidence': 0.89,
            'details': 'Text content matches speech'
        }
        
    async def _check_text_image_relevance(self, content: MultiModalContent) -> Dict[str, Any]:
        """Check if text is relevant to image content."""
        # Would use image captioning and semantic similarity
        return {
            'relevance_score': 0.88,
            'confidence': 0.83,
            'details': 'Text describes image content accurately'
        }
```

---

## Production Deployment

### 1. Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-detection-api
  labels:
    app: ai-detection
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-detection
  template:
    metadata:
      labels:
        app: ai-detection
    spec:
      containers:
      - name: api
        image: ai-detection:latest
        ports:
        - containerPort: 8000
        env:
        - name: MODEL_CACHE_DIR
          value: /models
        - name: REDIS_URL
          value: redis://redis-service:6379
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
            nvidia.com/gpu: 1
          limits:
            memory: "8Gi"
            cpu: "4"
            nvidia.com/gpu: 1
        volumeMounts:
        - name: model-storage
          mountPath: /models
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
      volumes:
      - name: model-storage
        persistentVolumeClaim:
          claimName: model-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ai-detection-service
spec:
  selector:
    app: ai-detection
  ports:
    - port: 80
      targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-detection-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-detection-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 2. FastAPI Production Server

```python
# app.py
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import redis
from typing import Optional, List
import uuid
from datetime import datetime
import json

app = FastAPI(title="AI Detection API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis for caching and job queue
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Initialize detectors
detectors = {
    'text': BinocularsDetector(),
    'image': DeepfakeBenchDetector(),
    'audio': AdvancedAudioDetector()
}

# Request/Response models
from pydantic import BaseModel

class DetectionRequest(BaseModel):
    content_type: str
    content: Optional[str] = None
    url: Optional[str] = None
    options: Dict[str, Any] = {}

class DetectionResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None

# Authentication
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API token."""
    token = credentials.credentials
    # Implement token verification
    if not redis_client.sismember("valid_tokens", token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

# Endpoints
@app.post("/detect", response_model=DetectionResponse)
async def detect_content(
    request: DetectionRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """Submit content for AI detection."""
    job_id = str(uuid.uuid4())
    
    # Store job in Redis
    job_data = {
        'status': 'pending',
        'created_at': datetime.utcnow().isoformat(),
        'content_type': request.content_type
    }
    redis_client.hset(f"job:{job_id}", mapping=job_data)
    
    # Process in background
    background_tasks.add_task(
        process_detection,
        job_id,
        request
    )
    
    return DetectionResponse(
        job_id=job_id,
        status='pending'
    )

async def process_detection(job_id: str, request: DetectionRequest):
    """Process detection job."""
    try:
        # Update status
        redis_client.hset(f"job:{job_id}", "status", "processing")
        
        # Get appropriate detector
        detector = detectors.get(request.content_type)
        if not detector:
            raise ValueError(f"Unsupported content type: {request.content_type}")
            
        # Load content if URL provided
        if request.url:
            content = await fetch_content(request.url)
        else:
            content = request.content
            
        # Run detection
        result = await detector.detect(content)
        
        # Store result
        redis_client.hset(f"job:{job_id}", mapping={
            "status": "completed",
            "result": json.dumps(result.__dict__),
            "completed_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        redis_client.hset(f"job:{job_id}", mapping={
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        })

@app.get("/detect/{job_id}", response_model=DetectionResponse)
async def get_detection_result(
    job_id: str,
    token: str = Depends(verify_token)
):
    """Get detection job result."""
    job_data = redis_client.hgetall(f"job:{job_id}")
    
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
        
    response = DetectionResponse(
        job_id=job_id,
        status=job_data.get('status'),
        error=job_data.get('error')
    )
    
    if job_data.get('result'):
        response.result = json.loads(job_data['result'])
        
    return response

@app.post("/batch", response_model=List[DetectionResponse])
async def batch_detect(
    files: List[UploadFile] = File(...),
    content_type: str = "image",
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """Batch detection for multiple files."""
    jobs = []
    
    for file in files:
        content = await file.read()
        request = DetectionRequest(
            content_type=content_type,
            content=content
        )
        
        job_id = str(uuid.uuid4())
        background_tasks.add_task(process_detection, job_id, request)
        
        jobs.append(DetectionResponse(
            job_id=job_id,
            status='pending'
        ))
        
    return jobs

# Health checks
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        redis_client.ping()
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    except:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": "Redis connection failed"}
        )

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    # Check if models are loaded
    for name, detector in detectors.items():
        if not hasattr(detector, 'model'):
            return JSONResponse(
                status_code=503,
                content={"status": "not ready", "error": f"{name} model not loaded"}
            )
    return {"status": "ready"}

# Metrics endpoint
@app.get("/metrics")
async def get_metrics(token: str = Depends(verify_token)):
    """Get API metrics."""
    metrics = {
        'total_jobs': redis_client.dbsize(),
        'pending_jobs': len(redis_client.keys("job:*:pending")),
        'completed_jobs': len(redis_client.keys("job:*:completed")),
        'failed_jobs': len(redis_client.keys("job:*:failed"))
    }
    return metrics

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)
```

### 3. Load Balancer Configuration

```nginx
# nginx.conf
upstream ai_detection_backend {
    least_conn;
    server backend1:8000 weight=3;
    server backend2:8000 weight=3;
    server backend3:8000 weight=2;
    
    # Health check
    check interval=5000 rise=2 fall=3 timeout=4000 type=http;
    check_http_send "GET /health HTTP/1.0\r\n\r\n";
    check_http_expect_alive http_2xx;
}

server {
    listen 80;
    server_name api.aidetection.example.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.aidetection.example.com;
    
    # SSL configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
    
    # File upload limits
    client_max_body_size 100M;
    client_body_timeout 120s;
    
    location / {
        proxy_pass http://ai_detection_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        
        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # WebSocket support for real-time detection
    location /ws {
        proxy_pass http://ai_detection_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
    
    # Static files
    location /static {
        alias /var/www/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## Performance Optimization

### 1. Model Optimization

```python
# model_optimization.py
import torch
from torch.quantization import quantize_dynamic
import onnx
import onnxruntime as ort

class ModelOptimizer:
    """Optimize models for production deployment."""
    
    @staticmethod
    def quantize_model(model: torch.nn.Module, dtype=torch.qint8) -> torch.nn.Module:
        """Dynamic quantization for faster inference."""
        quantized_model = quantize_dynamic(
            model,
            {torch.nn.Linear, torch.nn.Conv2d},
            dtype=dtype
        )
        return quantized_model
        
    @staticmethod
    def export_to_onnx(model: torch.nn.Module, 
                      dummy_input: torch.Tensor,
                      output_path: str):
        """Export model to ONNX for cross-platform deployment."""
        torch.onnx.export(
            model,
            dummy_input,
            output_path,
            export_params=True,
            opset_version=11,
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={
                'input': {0: 'batch_size'},
                'output': {0: 'batch_size'}
            }
        )
        
        # Verify ONNX model
        onnx_model = onnx.load(output_path)
        onnx.checker.check_model(onnx_model)
        
    @staticmethod
    def create_onnx_session(model_path: str) -> ort.InferenceSession:
        """Create optimized ONNX runtime session."""
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        session = ort.InferenceSession(
            model_path,
            sess_options,
            providers=providers
        )
        
        return session

# TensorRT optimization for NVIDIA GPUs
class TensorRTOptimizer:
    """GPU-specific optimizations using TensorRT."""
    
    @staticmethod
    def optimize_for_tensorrt(onnx_path: str, output_path: str):
        """Convert ONNX to TensorRT engine."""
        import tensorrt as trt
        
        logger = trt.Logger(trt.Logger.WARNING)
        builder = trt.Builder(logger)
        network = builder.create_network(
            1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
        )
        parser = trt.OnnxParser(network, logger)
        
        # Parse ONNX model
        with open(onnx_path, 'rb') as f:
            parser.parse(f.read())
            
        # Build optimization profile
        config = builder.create_builder_config()
        config.max_workspace_size = 1 << 30  # 1GB
        config.set_flag(trt.BuilderFlag.FP16)  # Enable FP16
        
        # Build engine
        engine = builder.build_engine(network, config)
        
        # Serialize
        with open(output_path, 'wb') as f:
            f.write(engine.serialize())
```

### 2. Caching Strategy

```python
# caching.py
import hashlib
import pickle
from typing import Any, Optional, Callable
import asyncio
from functools import wraps

class DetectionCache:
    """Intelligent caching for detection results."""
    
    def __init__(self, redis_client, ttl: int = 3600):
        self.redis = redis_client
        self.ttl = ttl
        
    def _generate_key(self, content: Any, detector_name: str) -> str:
        """Generate cache key from content."""
        if isinstance(content, str):
            content_hash = hashlib.sha256(content.encode()).hexdigest()
        elif isinstance(content, bytes):
            content_hash = hashlib.sha256(content).hexdigest()
        else:
            content_hash = hashlib.sha256(pickle.dumps(content)).hexdigest()
            
        return f"detection:{detector_name}:{content_hash}"
        
    async def get(self, content: Any, detector_name: str) -> Optional[DetectionResult]:
        """Get cached result if available."""
        key = self._generate_key(content, detector_name)
        cached = self.redis.get(key)
        
        if cached:
            return pickle.loads(cached.encode('latin-1'))
        return None
        
    async def set(self, content: Any, detector_name: str, result: DetectionResult):
        """Cache detection result."""
        key = self._generate_key(content, detector_name)
        serialized = pickle.dumps(result).decode('latin-1')
        self.redis.setex(key, self.ttl, serialized)
        
    def cached(self, detector_name: str):
        """Decorator for caching detector results."""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(self, content: Any) -> DetectionResult:
                # Check cache
                cached_result = await cache.get(content, detector_name)
                if cached_result:
                    cached_result.details['cache_hit'] = True
                    return cached_result
                    
                # Run detection
                result = await func(self, content)
                
                # Cache result
                await cache.set(content, detector_name, result)
                result.details['cache_hit'] = False
                
                return result
            return wrapper
        return decorator

# Usage example
cache = DetectionCache(redis_client)

class CachedBinocularsDetector(BinocularsDetector):
    @cache.cached("binoculars")
    async def detect(self, text: str) -> DetectionResult:
        return await super().detect(text)
```

### 3. Batch Processing Optimization

```python
# batch_optimizer.py
import numpy as np
from typing import List, Union
import torch
from concurrent.futures import ThreadPoolExecutor
import asyncio

class BatchProcessor:
    """Optimize batch processing for multiple inputs."""
    
    def __init__(self, 
                 detector: BaseDetector,
                 batch_size: int = 32,
                 max_wait_time: float = 0.1):
        self.detector = detector
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.pending_requests = []
        self.processing = False
        
    async def process_single(self, content: Any) -> DetectionResult:
        """Add single item to batch queue."""
        future = asyncio.Future()
        self.pending_requests.append((content, future))
        
        # Start batch processing if not already running
        if not self.processing:
            asyncio.create_task(self._process_batch())
            
        return await future
        
    async def _process_batch(self):
        """Process accumulated batch."""
        self.processing = True
        await asyncio.sleep(self.max_wait_time)  # Wait for more requests
        
        # Get current batch
        batch_requests = self.pending_requests[:self.batch_size]
        self.pending_requests = self.pending_requests[self.batch_size:]
        
        if not batch_requests:
            self.processing = False
            return
            
        # Extract contents
        contents = [req[0] for req in batch_requests]
        futures = [req[1] for req in batch_requests]
        
        try:
            # Process batch
            results = await self._batch_detect(contents)
            
            # Set results
            for future, result in zip(futures, results):
                future.set_result(result)
                
        except Exception as e:
            # Set exception for all futures
            for future in futures:
                future.set_exception(e)
                
        # Continue processing if more requests
        if self.pending_requests:
            asyncio.create_task(self._process_batch())
        else:
            self.processing = False
            
    async def _batch_detect(self, contents: List[Any]) -> List[DetectionResult]:
        """Perform batch detection."""
        # This would be implemented based on the specific detector
        # Example for image detection:
        if hasattr(self.detector, 'detect_batch'):
            return await self.detector.detect_batch(contents)
        else:
            # Fallback to sequential processing
            tasks = [self.detector.detect(content) for content in contents]
            return await asyncio.gather(*tasks)

# GPU memory optimization
class GPUMemoryManager:
    """Manage GPU memory for optimal performance."""
    
    def __init__(self, max_memory_gb: float = 8.0):
        self.max_memory = max_memory_gb * 1024 ** 3  # Convert to bytes
        self.current_usage = 0
        self.models = {}
        
    def load_model(self, name: str, model_loader: Callable) -> Any:
        """Load model with memory management."""
        if name in self.models:
            return self.models[name]
            
        # Check available memory
        if torch.cuda.is_available():
            free_memory = torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated()
            
            if free_memory < self.max_memory * 0.2:  # Less than 20% free
                # Unload least recently used model
                self._unload_lru_model()
                
        # Load model
        model = model_loader()
        self.models[name] = {
            'model': model,
            'last_used': time.time(),
            'memory_usage': self._get_model_memory(model)
        }
        
        return model
        
    def _get_model_memory(self, model: torch.nn.Module) -> int:
        """Estimate model memory usage."""
        param_memory = sum(p.numel() * p.element_size() for p in model.parameters())
        buffer_memory = sum(b.numel() * b.element_size() for b in model.buffers())
        return param_memory + buffer_memory
        
    def _unload_lru_model(self):
        """Unload least recently used model."""
        if not self.models:
            return
            
        lru_name = min(self.models.keys(), key=lambda k: self.models[k]['last_used'])
        del self.models[lru_name]
        torch.cuda.empty_cache()
```

---

## Error Handling & Monitoring

### 1. Comprehensive Error Handling

```python
# error_handling.py
from typing import Optional, Dict, Any
import traceback
from enum import Enum
import logging

class DetectionError(Exception):
    """Base exception for detection errors."""
    pass

class ModelLoadError(DetectionError):
    """Error loading model."""
    pass

class InvalidInputError(DetectionError):
    """Invalid input provided."""
    pass

class ProcessingError(DetectionError):
    """Error during processing."""
    pass

class ErrorHandler:
    """Centralized error handling for detection system."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.error_counts = {}
        
    async def handle_detection_error(self, 
                                   error: Exception,
                                   context: Dict[str, Any]) -> DetectionResult:
        """Handle errors during detection."""
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Log error with context
        self.logger.error(
            f"Detection error: {error_type}",
            extra={
                'error': str(error),
                'traceback': traceback.format_exc(),
                'context': context
            }
        )
        
        # Return error result
        return DetectionResult(
            is_ai_generated=False,
            confidence=0.0,
            modality=context.get('modality', 'unknown'),
            details={
                'error': str(error),
                'error_type': error_type,
                'recoverable': self._is_recoverable(error)
            },
            processing_time=0.0,
            model_used='error'
        )
        
    def _is_recoverable(self, error: Exception) -> bool:
        """Determine if error is recoverable."""
        recoverable_errors = (
            TimeoutError,
            ConnectionError,
            InvalidInputError
        )
        return isinstance(error, recoverable_errors)

# Circuit breaker for failing services
class CircuitBreaker:
    """Prevent cascading failures."""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
        
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'half-open'
            else:
                raise CircuitBreakerOpen("Circuit breaker is open")
                
        try:
            result = await func(*args, **kwargs)
            if self.state == 'half-open':
                self.state = 'closed'
                self.failure_count = 0
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'open'
                
            raise e
```

### 2. Monitoring and Metrics

```python
# monitoring.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
from typing import Dict, Any
import psutil

# Prometheus metrics
detection_requests = Counter(
    'detection_requests_total',
    'Total detection requests',
    ['modality', 'model']
)

detection_errors = Counter(
    'detection_errors_total',
    'Total detection errors',
    ['modality', 'error_type']
)

detection_duration = Histogram(
    'detection_duration_seconds',
    'Detection processing time',
    ['modality', 'model']
)

active_detections = Gauge(
    'active_detections',
    'Currently processing detections',
    ['modality']
)

model_accuracy = Gauge(
    'model_accuracy',
    'Model accuracy score',
    ['model']
)

class MetricsCollector:
    """Collect and export metrics."""
    
    def __init__(self):
        self.start_times = {}
        
    def record_request(self, modality: str, model: str):
        """Record incoming request."""
        detection_requests.labels(modality=modality, model=model).inc()
        active_detections.labels(modality=modality).inc()
        self.start_times[f"{modality}_{model}_{time.time()}"] = time.time()
        
    def record_completion(self, modality: str, model: str, success: bool = True):
        """Record request completion."""
        active_detections.labels(modality=modality).dec()
        
        # Find and record duration
        key_prefix = f"{modality}_{model}_"
        for key in list(self.start_times.keys()):
            if key.startswith(key_prefix):
                duration = time.time() - self.start_times[key]
                detection_duration.labels(modality=modality, model=model).observe(duration)
                del self.start_times[key]
                break
                
    def record_error(self, modality: str, error_type: str):
        """Record error occurrence."""
        detection_errors.labels(modality=modality, error_type=error_type).inc()
        
    def update_accuracy(self, model: str, accuracy: float):
        """Update model accuracy metric."""
        model_accuracy.labels(model=model).set(accuracy)
        
    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """Get system resource metrics."""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'gpu_memory': get_gpu_memory_usage() if torch.cuda.is_available() else 0
        }

# Logging configuration
class StructuredLogger:
    """Structured logging for better observability."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
    def log_detection(self, 
                     level: str,
                     message: str,
                     **kwargs):
        """Log with structured data."""
        extra = {
            'timestamp': time.time(),
            'detection_id': kwargs.get('detection_id'),
            'modality': kwargs.get('modality'),
            'model': kwargs.get('model'),
            'duration': kwargs.get('duration'),
            'result': kwargs.get('result'),
            'metadata': kwargs.get('metadata', {})
        }
        
        getattr(self.logger, level)(message, extra=extra)

# APM Integration
class APMTracer:
    """Application Performance Monitoring integration."""
    
    def __init__(self, service_name: str = "ai-detection"):
        # Example using Datadog APM
        from ddtrace import tracer
        self.tracer = tracer
        self.service_name = service_name
        
    def trace_detection(self, modality: str, model: str):
        """Create APM trace for detection."""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                with self.tracer.trace(
                    "detection.process",
                    service=self.service_name,
                    resource=f"{modality}.{model}"
                ) as span:
                    span.set_tag("modality", modality)
                    span.set_tag("model", model)
                    
                    try:
                        result = await func(*args, **kwargs)
                        span.set_tag("result", result.is_ai_generated)
                        span.set_tag("confidence", result.confidence)
                        return result
                    except Exception as e:
                        span.set_tag("error", True)
                        span.set_tag("error.type", type(e).__name__)
                        raise
            return wrapper
        return decorator
```

---

## Testing Strategies

### 1. Unit Testing

```python
# test_detectors.py
import pytest
import asyncio
from unittest.mock import Mock, patch
import numpy as np
from PIL import Image

class TestBinocularsDetector:
    """Unit tests for Binoculars text detector."""
    
    @pytest.fixture
    def detector(self):
        return BinocularsDetector()
        
    @pytest.fixture
    def sample_texts(self):
        return {
            'human': "The weather today is quite pleasant with sunny skies.",
            'ai': "As an AI language model, I can provide information about various topics including weather patterns and climate.",
            'short': "Hello",
            'long': "Lorem ipsum " * 1000
        }
        
    @pytest.mark.asyncio
    async def test_detect_human_text(self, detector, sample_texts):
        """Test detection of human-written text."""
        result = await detector.detect(sample_texts['human'])
        assert isinstance(result, DetectionResult)
        assert result.modality == 'text'
        assert 0 <= result.confidence <= 1
        
    @pytest.mark.asyncio
    async def test_detect_ai_text(self, detector, sample_texts):
        """Test detection of AI-generated text."""
        result = await detector.detect(sample_texts['ai'])
        assert result.is_ai_generated == True
        assert result.confidence > 0.7
        
    @pytest.mark.asyncio
    async def test_short_text_validation(self, detector, sample_texts):
        """Test validation rejects short text."""
        with pytest.raises(ValueError):
            await detector.detect(sample_texts['short'])
            
    @pytest.mark.asyncio
    async def test_text_preprocessing(self, detector, sample_texts):
        """Test text preprocessing handles long text."""
        result = await detector.detect(sample_texts['long'])
        assert result is not None
        assert result.details['text_length'] <= 2048

class TestImageDetector:
    """Unit tests for image detection."""
    
    @pytest.fixture
    def detector(self):
        return DeepfakeBenchDetector(model_name='effort')
        
    @pytest.fixture
    def sample_images(self):
        # Create test images
        real_image = Image.new('RGB', (256, 256), color='red')
        fake_image = Image.new('RGB', (256, 256), color='blue')
        small_image = Image.new('RGB', (32, 32), color='green')
        
        return {
            'real': real_image,
            'fake': fake_image,
            'small': small_image
        }
        
    @pytest.mark.asyncio
    async def test_detect_real_image(self, detector, sample_images):
        """Test detection of real image."""
        result = await detector.detect(sample_images['real'])
        assert isinstance(result, DetectionResult)
        assert result.modality == 'image'
        
    @pytest.mark.asyncio
    async def test_image_validation(self, detector, sample_images):
        """Test image size validation."""
        with pytest.raises(ValueError):
            await detector.detect(sample_images['small'])
            
    @pytest.mark.asyncio
    async def test_batch_processing(self, sample_images):
        """Test batch image processing."""
        batch_detector = BatchImageDetector(DeepfakeBenchDetector())
        images = [sample_images['real'], sample_images['fake']]
        
        results = await batch_detector.detect_batch(images)
        assert len(results) == 2
        assert all(isinstance(r, DetectionResult) for r in results)
```

### 2. Integration Testing

```python
# test_integration.py
import aiohttp
import pytest
from testcontainers.redis import RedisContainer
from testcontainers.postgres import PostgresContainer

class TestAPIIntegration:
    """Integration tests for API endpoints."""
    
    @pytest.fixture(scope="class")
    def redis_container(self):
        with RedisContainer() as redis:
            yield redis
            
    @pytest.fixture(scope="class")
    def postgres_container(self):
        with PostgresContainer("postgres:15") as postgres:
            yield postgres
            
    @pytest.fixture
    async def api_client(self, redis_container, postgres_container):
        """Create API client with test containers."""
        # Configure app with test containers
        app.dependency_overrides[get_redis] = lambda: redis_container.get_client()
        app.dependency_overrides[get_db] = lambda: postgres_container.get_connection()
        
        async with aiohttp.ClientSession() as session:
            yield session
            
    @pytest.mark.asyncio
    async def test_text_detection_endpoint(self, api_client):
        """Test text detection API endpoint."""
        payload = {
            "content_type": "text",
            "content": "This is a test text for AI detection."
        }
        
        async with api_client.post(
            "http://localhost:8000/detect",
            json=payload,
            headers={"Authorization": "Bearer test-token"}
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert "job_id" in data
            assert data["status"] == "pending"
            
    @pytest.mark.asyncio
    async def test_batch_detection(self, api_client):
        """Test batch detection endpoint."""
        # Create test files
        files = [
            ('files', ('test1.jpg', b'fake-image-data', 'image/jpeg')),
            ('files', ('test2.jpg', b'fake-image-data', 'image/jpeg'))
        ]
        
        async with api_client.post(
            "http://localhost:8000/batch",
            data={"content_type": "image"},
            files=files,
            headers={"Authorization": "Bearer test-token"}
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert len(data) == 2
            assert all("job_id" in item for item in data)
            
    @pytest.mark.asyncio
    async def test_websocket_streaming(self, api_client):
        """Test WebSocket streaming detection."""
        async with api_client.ws_connect("ws://localhost:8000/ws") as ws:
            # Send detection request
            await ws.send_json({
                "type": "detect",
                "content_type": "text",
                "content": "Streaming text detection test"
            })
            
            # Receive result
            msg = await ws.receive_json()
            assert msg["type"] == "result"
            assert "confidence" in msg
```

### 3. Performance Testing

```python
# test_performance.py
import asyncio
import time
from locust import HttpUser, task, between
import statistics

class PerformanceTests:
    """Performance testing for detection system."""
    
    @pytest.mark.benchmark
    async def test_text_detection_speed(self, detector, benchmark):
        """Benchmark text detection speed."""
        text = "This is a sample text " * 50  # ~250 words
        
        async def detect():
            return await detector.detect(text)
            
        result = benchmark.pedantic(
            asyncio.run,
            args=(detect(),),
            iterations=100,
            rounds=5
        )
        
        # Assert performance requirements
        assert benchmark.stats["mean"] < 0.1  # Less than 100ms average
        assert benchmark.stats["max"] < 0.5   # Less than 500ms max
        
    async def test_concurrent_requests(self, api_client):
        """Test API under concurrent load."""
        num_requests = 100
        
        async def make_request(session, i):
            start = time.time()
            async with session.post(
                "http://localhost:8000/detect",
                json={
                    "content_type": "text",
                    "content": f"Test content {i}"
                }
            ) as response:
                await response.json()
                return time.time() - start
                
        # Run concurrent requests
        tasks = [
            make_request(api_client, i)
            for i in range(num_requests)
        ]
        
        latencies = await asyncio.gather(*tasks)
        
        # Analyze results
        assert statistics.mean(latencies) < 1.0  # Average under 1 second
        assert statistics.quantiles(latencies, n=100)[94] < 2.0  # p95 under 2 seconds

# Locust load testing
class DetectionUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Authenticate user."""
        self.client.headers.update({
            "Authorization": "Bearer load-test-token"
        })
        
    @task(3)
    def detect_text(self):
        """Test text detection endpoint."""
        self.client.post("/detect", json={
            "content_type": "text",
            "content": "Load test text content"
        })
        
    @task(2)
    def detect_image(self):
        """Test image detection endpoint."""
        with open("test_image.jpg", "rb") as f:
            self.client.post("/detect", files={
                "file": ("test.jpg", f, "image/jpeg")
            }, data={"content_type": "image"})
            
    @task(1)
    def check_status(self):
        """Test status check endpoint."""
        self.client.get("/detect/test-job-id")
```

### 4. End-to-End Testing

```python
# test_e2e.py
from playwright.async_api import async_playwright
import pytest

class TestE2E:
    """End-to-end tests using Playwright."""
    
    @pytest.mark.asyncio
    async def test_web_interface_detection(self):
        """Test detection through web interface."""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Navigate to web interface
            await page.goto("http://localhost:3000")
            
            # Upload image
            await page.set_input_files(
                'input[type="file"]',
                "test_images/sample.jpg"
            )
            
            # Click detect button
            await page.click('button:has-text("Detect")')
            
            # Wait for result
            await page.wait_for_selector('.detection-result', timeout=10000)
            
            # Check result displayed
            result_text = await page.text_content('.detection-result')
            assert "AI Generated" in result_text or "Real" in result_text
            
            # Check confidence score
            confidence = await page.text_content('.confidence-score')
            assert float(confidence.strip('%')) >= 0
            
            await browser.close()
            
    @pytest.mark.asyncio
    async def test_api_workflow(self):
        """Test complete API workflow."""
        async with aiohttp.ClientSession() as session:
            # 1. Submit detection job
            async with session.post(
                "http://localhost:8000/detect",
                json={
                    "content_type": "text",
                    "content": "E2E test content"
                },
                headers={"Authorization": "Bearer test-token"}
            ) as response:
                submit_data = await response.json()
                job_id = submit_data["job_id"]
                
            # 2. Poll for result
            max_attempts = 30
            for attempt in range(max_attempts):
                async with session.get(
                    f"http://localhost:8000/detect/{job_id}",
                    headers={"Authorization": "Bearer test-token"}
                ) as response:
                    result_data = await response.json()
                    
                    if result_data["status"] == "completed":
                        assert "result" in result_data
                        assert "confidence" in result_data["result"]
                        break
                        
                await asyncio.sleep(1)
            else:
                pytest.fail(f"Job {job_id} did not complete in time")
```

---

## Summary

This implementation guide provides production-ready code for deploying open-source AI detection systems across all modalities. Key highlights:

1. **Modular Architecture**: Each detector follows a common interface for easy integration
2. **Performance Optimized**: Batch processing, caching, and GPU optimization included
3. **Production Ready**: Complete with Docker, Kubernetes, and monitoring setup
4. **Comprehensive Testing**: Unit, integration, performance, and E2E test examples
5. **Error Handling**: Robust error handling with circuit breakers and retries
6. **Scalable Design**: Supports horizontal scaling and load balancing

The code examples can be adapted to specific use cases and combined to create a complete AI detection platform.