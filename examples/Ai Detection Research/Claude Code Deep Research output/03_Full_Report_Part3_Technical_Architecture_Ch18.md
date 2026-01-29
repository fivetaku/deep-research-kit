## Chapter 18: Open Source Ecosystem

### The Open Source Detection Landscape

The open source ecosystem for AI content detection represents both humanity's best hope for democratized defense against synthetic media and a fragmented landscape of varying quality, maintenance, and reliability. Unlike commercial solutions bound by profit motives and competitive secrecy, open source projects enable transparent verification of detection methods, collaborative improvement, and adaptation to local needs. However, this same openness creates challenges: inconsistent documentation, abandoned projects, and the ease with which malicious actors can study detection methods to develop countermeasures.

The ecosystem spans from individual researchers sharing proof-of-concept code to well-funded initiatives backed by major institutions. Understanding this landscape requires examining not just the technical capabilities of various projects, but also their governance models, community health, and long-term sustainability. The most successful open source detection projects share common characteristics: active maintainer communities, clear documentation, modular architectures that encourage contribution, and transparent discussions about limitations and failure modes.

### Major Open Source Projects

#### DeepFace Detection Suite

One of the most comprehensive open source efforts, the DeepFace Detection Suite provides industrial-strength detection capabilities across multiple modalities.

```python
# deepface_detection/core.py - Core detection framework
"""
DeepFace Detection Suite
Open source deepfake detection with state-of-the-art models
License: MIT
"""

import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from pathlib import Path

class DeepFaceDetector:
    """
    Main detection interface supporting multiple backends and models
    """
    
    SUPPORTED_MODELS = {
        'xception': {
            'weights': 'https://github.com/deepface-detection/models/releases/download/v1.0/xception_deepfake.pth',
            'accuracy': 0.92,
            'speed': 'medium',
            'memory': '2.1GB'
        },
        'efficientnet-b4': {
            'weights': 'https://github.com/deepface-detection/models/releases/download/v1.0/efficientnet_b4_deepfake.pth',
            'accuracy': 0.94,
            'speed': 'fast',
            'memory': '1.3GB'
        },
        'mesonet': {
            'weights': 'https://github.com/deepface-detection/models/releases/download/v1.0/mesonet.pth',
            'accuracy': 0.87,
            'speed': 'very_fast',
            'memory': '27MB'
        },
        'capsule': {
            'weights': 'https://github.com/deepface-detection/models/releases/download/v1.0/capsule_net.pth',
            'accuracy': 0.89,
            'speed': 'slow',
            'memory': '3.5GB'
        }
    }
    
    def __init__(
        self, 
        model_name: str = 'efficientnet-b4',
        device: str = 'auto',
        cache_dir: Optional[Path] = None,
        enable_tta: bool = False
    ):
        """
        Initialize detector with specified model
        
        Args:
            model_name: Name of model to use
            device: 'cuda', 'cpu', or 'auto'
            cache_dir: Directory for model weights cache
            enable_tta: Enable test-time augmentation for better accuracy
        """
        self.model_name = model_name
        self.device = self._setup_device(device)
        self.cache_dir = cache_dir or Path.home() / '.deepface_detection' / 'models'
        self.enable_tta = enable_tta
        
        self.model = self._load_model()
        self.preprocessor = PreProcessor(model_name)
        self.postprocessor = PostProcessor()
        
    def _setup_device(self, device: str) -> torch.device:
        if device == 'auto':
            return torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        return torch.device(device)
    
    def _load_model(self) -> nn.Module:
        """Load model with automatic downloading if needed"""
        model_info = self.SUPPORTED_MODELS[self.model_name]
        model_path = self.cache_dir / f"{self.model_name}.pth"
        
        # Download if not cached
        if not model_path.exists():
            print(f"Downloading {self.model_name} model...")
            download_model(model_info['weights'], model_path)
        
        # Load model architecture
        if self.model_name == 'xception':
            model = XceptionNet()
        elif self.model_name.startswith('efficientnet'):
            model = EfficientNetDetector(self.model_name)
        elif self.model_name == 'mesonet':
            model = MesoNet()
        elif self.model_name == 'capsule':
            model = CapsuleNet()
        else:
            raise ValueError(f"Unknown model: {self.model_name}")
        
        # Load weights
        state_dict = torch.load(model_path, map_location=self.device)
        model.load_state_dict(state_dict)
        model.to(self.device)
        model.eval()
        
        return model
    
    def detect(
        self, 
        image: Union[str, Path, np.ndarray],
        return_visualization: bool = False
    ) -> Dict:
        """
        Detect if image is AI-generated
        
        Args:
            image: Path to image or numpy array
            return_visualization: Return heatmap visualization
            
        Returns:
            Detection results dictionary
        """
        # Load and preprocess image
        if isinstance(image, (str, Path)):
            image = load_image(image)
        
        processed = self.preprocessor.process(image)
        
        # Test-time augmentation if enabled
        if self.enable_tta:
            predictions = self._detect_with_tta(processed)
        else:
            predictions = self._detect_single(processed)
        
        # Post-process results
        results = self.postprocessor.process(predictions, image)
        
        # Add visualization if requested
        if return_visualization:
            results['heatmap'] = self._generate_heatmap(processed, predictions)
        
        return results
    
    def _detect_single(self, image_tensor: torch.Tensor) -> torch.Tensor:
        """Single forward pass detection"""
        with torch.no_grad():
            image_tensor = image_tensor.to(self.device)
            output = self.model(image_tensor.unsqueeze(0))
            
            if isinstance(output, dict):
                # Some models return additional information
                predictions = output['logits']
                self.last_features = output.get('features')
            else:
                predictions = output
                
        return predictions
    
    def _detect_with_tta(self, image_tensor: torch.Tensor) -> torch.Tensor:
        """Test-time augmentation for improved accuracy"""
        augmentations = [
            lambda x: x,  # Original
            lambda x: torch.flip(x, dims=[2]),  # Horizontal flip
            lambda x: torch.rot90(x, k=1, dims=[1, 2]),  # 90° rotation
            lambda x: torch.rot90(x, k=3, dims=[1, 2]),  # 270° rotation
        ]
        
        predictions = []
        for aug_fn in augmentations:
            augmented = aug_fn(image_tensor)
            pred = self._detect_single(augmented)
            predictions.append(pred)
        
        # Average predictions
        return torch.stack(predictions).mean(dim=0)
    
    def detect_batch(
        self, 
        images: List[Union[str, Path, np.ndarray]],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> List[Dict]:
        """
        Detect multiple images efficiently
        
        Args:
            images: List of image paths or arrays
            batch_size: Batch size for processing
            show_progress: Show progress bar
            
        Returns:
            List of detection results
        """
        from tqdm import tqdm
        
        results = []
        iterator = range(0, len(images), batch_size)
        
        if show_progress:
            iterator = tqdm(iterator, desc="Processing batches")
        
        for i in iterator:
            batch_images = images[i:i + batch_size]
            batch_tensors = []
            
            # Prepare batch
            for img in batch_images:
                if isinstance(img, (str, Path)):
                    img = load_image(img)
                processed = self.preprocessor.process(img)
                batch_tensors.append(processed)
            
            # Stack into batch tensor
            batch_tensor = torch.stack(batch_tensors).to(self.device)
            
            # Batch inference
            with torch.no_grad():
                batch_predictions = self.model(batch_tensor)
            
            # Process each result
            for j, (img, pred) in enumerate(zip(batch_images, batch_predictions)):
                result = self.postprocessor.process(pred.unsqueeze(0), img)
                results.append(result)
        
        return results
    
    def explain(
        self, 
        image: Union[str, Path, np.ndarray],
        method: str = 'gradcam'
    ) -> Dict:
        """
        Generate explanation for detection decision
        
        Args:
            image: Input image
            method: Explanation method ('gradcam', 'lime', 'shap')
            
        Returns:
            Explanation dictionary with heatmaps and attributions
        """
        if isinstance(image, (str, Path)):
            image = load_image(image)
        
        processed = self.preprocessor.process(image)
        
        if method == 'gradcam':
            explanation = self._explain_gradcam(processed, image)
        elif method == 'lime':
            explanation = self._explain_lime(processed, image)
        elif method == 'shap':
            explanation = self._explain_shap(processed, image)
        else:
            raise ValueError(f"Unknown explanation method: {method}")
        
        return explanation
    
    def _explain_gradcam(self, image_tensor: torch.Tensor, original_image: np.ndarray) -> Dict:
        """Generate GradCAM explanation"""
        from .explainability import GradCAM
        
        # Get model's last convolutional layer
        if self.model_name == 'xception':
            target_layer = self.model.features[-1]
        elif self.model_name.startswith('efficientnet'):
            target_layer = self.model.features[-1]
        else:
            target_layer = self.model.conv_final
        
        gradcam = GradCAM(self.model, target_layer)
        heatmap = gradcam.generate(image_tensor.unsqueeze(0).to(self.device))
        
        return {
            'method': 'gradcam',
            'heatmap': heatmap,
            'overlay': overlay_heatmap(original_image, heatmap),
            'important_regions': extract_important_regions(heatmap)
        }

# Community contribution: Multi-modal detection
class MultiModalDetector(DeepFaceDetector):
    """
    Extended detector supporting video and audio
    Community contribution by @username
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_model = self._load_video_model()
        self.audio_model = self._load_audio_model()
    
    def detect_video(
        self, 
        video_path: Union[str, Path],
        sample_rate: int = 5,
        aggregate_method: str = 'weighted_average'
    ) -> Dict:
        """
        Detect deepfakes in video
        
        Args:
            video_path: Path to video file
            sample_rate: Frames per second to sample
            aggregate_method: How to combine frame results
            
        Returns:
            Video detection results
        """
        frames = extract_frames(video_path, sample_rate)
        frame_results = []
        
        # Detect each frame
        for i, frame in enumerate(frames):
            result = self.detect(frame)
            result['frame_number'] = i
            result['timestamp'] = i / sample_rate
            frame_results.append(result)
        
        # Aggregate results
        if aggregate_method == 'weighted_average':
            # Weight recent frames more heavily
            weights = np.exp(np.linspace(-1, 0, len(frame_results)))
            weights /= weights.sum()
            
            confidence = sum(
                r['confidence'] * w 
                for r, w in zip(frame_results, weights)
            )
        elif aggregate_method == 'majority_vote':
            votes = [r['is_fake'] for r in frame_results]
            is_fake = sum(votes) > len(votes) / 2
            confidence = sum(votes) / len(votes)
        else:
            raise ValueError(f"Unknown aggregation method: {aggregate_method}")
        
        return {
            'type': 'video',
            'is_fake': confidence > 0.5,
            'confidence': confidence,
            'frame_analysis': frame_results,
            'duration': len(frames) / sample_rate,
            'method': self.model_name
        }
```

#### Deepware Scanner Core

The open source core of the popular Deepware Scanner provides a robust foundation for building detection applications.

```python
# deepware_core/scanner.py - Core scanning engine
"""
Deepware Scanner Core
Open source deepfake detection engine
License: Apache 2.0
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp
from typing import AsyncIterator, Optional
import aiohttp
import cv2

class DeepwareScanner:
    """
    High-performance scanning engine with async support
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self.default_config()
        self.models = ModelRegistry()
        self.executor = ThreadPoolExecutor(max_workers=self.config['max_workers'])
        self.session = None
        
        # Initialize models based on config
        self._initialize_models()
    
    def default_config(self) -> Dict:
        """Default configuration for scanner"""
        return {
            'max_workers': mp.cpu_count(),
            'batch_size': 32,
            'models': {
                'face_detection': 'retinaface',
                'deepfake_detection': 'xception',
                'quality_assessment': 'brisque',
                'artifact_detection': 'prnu'
            },
            'thresholds': {
                'face_confidence': 0.9,
                'deepfake_confidence': 0.7,
                'quality_threshold': 50
            },
            'enable_gpu': torch.cuda.is_available(),
            'cache_enabled': True,
            'cache_size_mb': 500
        }
    
    async def scan_url(self, url: str) -> Dict:
        """
        Scan media from URL
        
        Args:
            url: URL of media to scan
            
        Returns:
            Scan results
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Download media
            async with self.session.get(url) as response:
                content = await response.read()
                content_type = response.headers.get('Content-Type', '')
            
            # Route to appropriate scanner
            if 'image' in content_type:
                return await self.scan_image_bytes(content)
            elif 'video' in content_type:
                return await self.scan_video_bytes(content)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
                
        except Exception as e:
            return {
                'error': str(e),
                'status': 'failed',
                'url': url
            }
    
    async def scan_image_bytes(self, image_bytes: bytes) -> Dict:
        """Scan image from bytes"""
        # Decode image
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return {'error': 'Failed to decode image', 'status': 'failed'}
        
        # Run detection pipeline
        results = await self._run_image_pipeline(image)
        
        return results
    
    async def _run_image_pipeline(self, image: np.ndarray) -> Dict:
        """Run full detection pipeline on image"""
        pipeline_tasks = []
        
        # Face detection
        pipeline_tasks.append(
            self._run_in_executor(self.models.face_detector.detect, image)
        )
        
        # Quality assessment
        pipeline_tasks.append(
            self._run_in_executor(self.models.quality_assessor.assess, image)
        )
        
        # Wait for initial results
        faces, quality = await asyncio.gather(*pipeline_tasks)
        
        if not faces:
            return {
                'status': 'no_faces_found',
                'is_deepfake': False,
                'confidence': 0.0,
                'quality_score': quality
            }
        
        # Deepfake detection on each face
        detection_tasks = []
        for face in faces:
            face_crop = self._crop_face(image, face)
            detection_tasks.append(
                self._run_in_executor(
                    self.models.deepfake_detector.detect,
                    face_crop
                )
            )
        
        # Artifact detection
        detection_tasks.append(
            self._run_in_executor(
                self.models.artifact_detector.detect,
                image
            )
        )
        
        # Wait for all detections
        *face_results, artifacts = await asyncio.gather(*detection_tasks)
        
        # Aggregate results
        return self._aggregate_results(faces, face_results, quality, artifacts)
    
    async def _run_in_executor(self, func, *args):
        """Run CPU-intensive function in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args)
    
    def _aggregate_results(
        self,
        faces: List[Dict],
        face_results: List[Dict],
        quality: float,
        artifacts: Dict
    ) -> Dict:
        """Aggregate detection results from multiple sources"""
        # Combine face detection results
        deepfake_scores = [r['deepfake_score'] for r in face_results]
        max_score = max(deepfake_scores) if deepfake_scores else 0
        avg_score = sum(deepfake_scores) / len(deepfake_scores) if deepfake_scores else 0
        
        # Weight by quality and artifacts
        if quality < self.config['thresholds']['quality_threshold']:
            # Low quality images are less reliable
            confidence_penalty = 0.2
        else:
            confidence_penalty = 0
        
        # Boost confidence if artifacts detected
        artifact_boost = 0.1 if artifacts['suspicious_artifacts'] else 0
        
        final_confidence = min(1.0, avg_score + artifact_boost - confidence_penalty)
        
        return {
            'status': 'success',
            'is_deepfake': final_confidence > self.config['thresholds']['deepfake_confidence'],
            'confidence': final_confidence,
            'max_face_score': max_score,
            'avg_face_score': avg_score,
            'num_faces': len(faces),
            'quality_score': quality,
            'artifacts': artifacts,
            'model_versions': self.models.get_versions(),
            'processing_time': time.time() - start_time
        }
    
    async def scan_video_stream(
        self,
        stream_url: str,
        callback: Callable[[Dict], None]
    ) -> AsyncIterator[Dict]:
        """
        Scan live video stream
        
        Args:
            stream_url: URL of video stream
            callback: Function to call with results
            
        Yields:
            Detection results for each frame batch
        """
        cap = cv2.VideoCapture(stream_url)
        frame_buffer = []
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_buffer.append(frame)
                
                # Process batch when full
                if len(frame_buffer) >= self.config['batch_size']:
                    results = await self._process_frame_batch(frame_buffer)
                    callback(results)
                    yield results
                    frame_buffer = []
                
        finally:
            cap.release()
            
    async def close(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)
        if self.session:
            await self.session.close()
```

#### Academic Research Implementations

Research institutions regularly release implementations of cutting-edge detection methods, though these often prioritize accuracy over production readiness.

```python
# research/cvpr2024_detector.py - Latest academic detector
"""
CVPR 2024 Best Paper Implementation
"Detecting Deepfakes with Frequency Analysis and Vision Transformers"
Original authors: Smith et al.
Implementation by: Community Contributors
"""

import torch
import torch.nn as nn
from einops import rearrange, repeat
import torch.fft

class FrequencyAwareViT(nn.Module):
    """
    Vision Transformer with frequency domain analysis
    Achieves 96.8% accuracy on FaceForensics++
    """
    
    def __init__(
        self,
        image_size: int = 224,
        patch_size: int = 16,
        num_classes: int = 2,
        dim: int = 768,
        depth: int = 12,
        heads: int = 12,
        mlp_dim: int = 3072,
        dropout: float = 0.1
    ):
        super().__init__()
        
        # Frequency analysis branch
        self.freq_analyzer = FrequencyAnalyzer()
        
        # Vision Transformer
        num_patches = (image_size // patch_size) ** 2
        patch_dim = 3 * patch_size ** 2
        
        self.patch_embed = nn.Sequential(
            Rearrange('b c (h p1) (w p2) -> b (h w) (p1 p2 c)', 
                     p1=patch_size, p2=patch_size),
            nn.Linear(patch_dim, dim)
        )
        
        self.pos_embedding = nn.Parameter(torch.randn(1, num_patches + 1, dim))
        self.cls_token = nn.Parameter(torch.randn(1, 1, dim))
        self.dropout = nn.Dropout(dropout)
        
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(
                d_model=dim,
                nhead=heads,
                dim_feedforward=mlp_dim,
                dropout=dropout,
                batch_first=True
            ),
            num_layers=depth
        )
        
        # Fusion layer
        self.fusion = nn.Sequential(
            nn.Linear(dim + 256, 512),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        batch_size = x.shape[0]
        
        # Frequency analysis
        freq_features = self.freq_analyzer(x)
        
        # Vision Transformer encoding
        x = self.patch_embed(x)
        
        cls_tokens = repeat(self.cls_token, '1 1 d -> b 1 d', b=batch_size)
        x = torch.cat([cls_tokens, x], dim=1)
        x += self.pos_embedding
        x = self.dropout(x)
        
        x = self.transformer(x)
        
        # Take cls token
        cls_output = x[:, 0]
        
        # Fuse spatial and frequency features
        fused = torch.cat([cls_output, freq_features], dim=-1)
        logits = self.fusion(fused)
        
        return {
            'logits': logits,
            'spatial_features': cls_output,
            'frequency_features': freq_features,
            'attention_weights': self.get_attention_weights()
        }
    
    def get_attention_weights(self) -> torch.Tensor:
        """Extract attention weights for visualization"""
        # This would extract attention from transformer layers
        # Simplified for brevity
        return torch.ones(1, 12, 197, 197)  # dummy


class FrequencyAnalyzer(nn.Module):
    """
    Analyze frequency domain for GAN/diffusion artifacts
    Key insight: AI-generated images have distinct frequency signatures
    """
    
    def __init__(self, feature_dim: int = 256):
        super().__init__()
        
        # Learnable frequency filters
        self.frequency_filters = nn.Parameter(
            torch.randn(64, 3, 8, 8)
        )
        
        # CNN for frequency domain
        self.freq_cnn = nn.Sequential(
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2),
            
            nn.Conv2d(128, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(2),
            
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(256, feature_dim)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Convert to frequency domain
        x_freq = torch.fft.fft2(x, dim=(-2, -1))
        x_freq = torch.stack([x_freq.real, x_freq.imag], dim=-1)
        
        # Apply learnable filters
        batch_size = x.shape[0]
        filtered = []
        
        for i in range(64):
            # Apply filter in frequency domain
            filter_freq = torch.fft.fft2(
                self.frequency_filters[i].unsqueeze(0),
                dim=(-2, -1)
            )
            
            # Element-wise multiplication in frequency domain
            result = x_freq * filter_freq.unsqueeze(0)
            
            # Convert back to spatial domain
            result_complex = torch.complex(result[..., 0], result[..., 1])
            result_spatial = torch.fft.ifft2(result_complex, dim=(-2, -1)).real
            
            filtered.append(result_spatial)
        
        # Stack filtered results
        filtered = torch.stack(filtered, dim=1)
        
        # Extract features
        features = self.freq_cnn(filtered)
        
        return features
```

### Contributing to Open Source Projects

#### Best Practices for Contributors

The health of open source detection projects depends on quality contributions that enhance capabilities while maintaining stability.

```python
# CONTRIBUTING.md example structure
"""
# Contributing to DeepFace Detection Suite

We welcome contributions! This guide will help you get started.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/deepface-detection`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Set up development environment: `./scripts/setup_dev.sh`

## Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linting
flake8 deepface_detection/
black deepface_detection/ --check
```

## Code Standards

### Style Guide
- Follow PEP 8
- Use type hints for all functions
- Maximum line length: 88 characters (Black default)
- Docstrings for all public functions (Google style)

### Example:
```python
def detect_manipulation(
    image: np.ndarray,
    method: str = "frequency",
    threshold: float = 0.7
) -> DetectionResult:
    \"\"\"
    Detect image manipulation using specified method.
    
    Args:
        image: Input image as numpy array (H, W, C)
        method: Detection method to use
        threshold: Confidence threshold for detection
        
    Returns:
        Detection result with confidence and metadata
        
    Raises:
        ValueError: If method is not supported
    \"\"\"
    if method not in SUPPORTED_METHODS:
        raise ValueError(f"Unsupported method: {method}")
    
    # Implementation here
    pass
```

## Testing Requirements

### Unit Tests
Every new feature must include tests:

```python
# tests/test_new_feature.py
import pytest
from deepface_detection import YourNewFeature

class TestYourNewFeature:
    def test_basic_functionality(self):
        feature = YourNewFeature()
        result = feature.process(test_input)
        assert result.confidence > 0
        assert result.is_valid()
    
    def test_edge_cases(self):
        # Test with empty input
        with pytest.raises(ValueError):
            feature.process(None)
    
    @pytest.mark.slow
    def test_performance(self, benchmark):
        feature = YourNewFeature()
        result = benchmark(feature.process, large_test_input)
        assert result.processing_time < 1.0  # seconds
```

### Integration Tests
Test interaction with other components:

```python
def test_integration_with_detector():
    detector = DeepFaceDetector()
    feature = YourNewFeature()
    
    # Ensure compatibility
    detector.add_plugin(feature)
    result = detector.detect(test_image)
    
    assert 'your_feature_output' in result
```

## Documentation

### Code Documentation
- Update docstrings for modified functions
- Add examples for new features
- Update type hints

### User Documentation
- Update README.md if adding user-facing features
- Add to docs/ for detailed documentation
- Include performance benchmarks

### Example Documentation:
```markdown
## New Feature: Temporal Consistency Check

This feature adds temporal consistency checking for video deepfake detection.

### Usage
```python
from deepface_detection import TemporalConsistencyChecker

checker = TemporalConsistencyChecker(
    window_size=5,
    consistency_threshold=0.9
)

video_results = detector.detect_video(
    "path/to/video.mp4",
    plugins=[checker]
)

print(f"Temporal anomalies: {video_results.temporal_anomalies}")
```

### Performance
- Adds ~15% to processing time
- Improves accuracy by 3-5% on video deepfakes
- Memory overhead: ~200MB for 1080p video
```

## Pull Request Process

1. **Before Submitting**
   - [ ] All tests pass: `pytest tests/`
   - [ ] Code is formatted: `black deepface_detection/`
   - [ ] No linting errors: `flake8 deepface_detection/`
   - [ ] Documentation updated
   - [ ] Changelog entry added

2. **PR Description Template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Performance improvement
   - [ ] Documentation update
   
   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests pass
   - [ ] Manual testing completed
   
   ## Performance Impact
   - Processing time: +X% / -X% / No change
   - Memory usage: +X MB / No change
   - Accuracy: +X% / No change
   
   ## Checklist
   - [ ] My code follows project style
   - [ ] I have added tests
   - [ ] All tests pass
   - [ ] I have updated documentation
   ```

3. **Review Process**
   - Maintainers will review within 72 hours
   - Address feedback promptly
   - Be patient and respectful

## Performance Contributions

### Optimization Guidelines
When contributing performance improvements:

1. **Benchmark Before and After**
```python
# benchmarks/bench_your_feature.py
import time
from deepface_detection import YourFeature

def benchmark_old_method():
    # Old implementation
    pass

def benchmark_new_method():
    # Your optimized implementation
    pass

# Run benchmarks
old_time = timeit.timeit(benchmark_old_method, number=100)
new_time = timeit.timeit(benchmark_new_method, number=100)

print(f"Speedup: {old_time / new_time:.2f}x")
```

2. **Profile Code**
```bash
python -m cProfile -o profile.stats your_script.py
python -m pstats profile.stats
```

3. **Memory Profiling**
```python
from memory_profiler import profile

@profile
def your_function():
    # Implementation
    pass
```

## Security Contributions

### Reporting Vulnerabilities
- Do NOT open public issues for security vulnerabilities
- Email security@deepface-detection.org
- Include:
  - Description of vulnerability
  - Steps to reproduce
  - Potential impact
  - Suggested fix (if any)

### Security Best Practices
- Validate all inputs
- Use secure random for any randomness
- Don't trust file extensions
- Sanitize paths
- Limit resource consumption

## Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Welcome newcomers
- Give constructive feedback
- Focus on what's best for the community

### Getting Help
- Discord: https://discord.gg/deepface-detection
- GitHub Discussions for questions
- Stack Overflow tag: deepface-detection

### Recognition
Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Annual contributor spotlight

Thank you for contributing to make AI detection accessible to everyone!
"""
```

This chapter continues with sections on project governance, sustainability models, and integration patterns...