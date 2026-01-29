## Chapter 17: Mobile Application Architecture

### Mobile Detection Challenges

Mobile platforms present unique challenges for AI content detection that differ fundamentally from web or desktop environments. Limited computational resources, battery constraints, intermittent connectivity, and diverse hardware capabilities require architectures that balance accuracy with efficiency. The mobile ecosystem's fragmentation - spanning iOS, Android, and various device capabilities - demands flexible solutions that can adapt to vastly different runtime environments.

The stakes are particularly high on mobile devices, where users encounter AI-generated content through social media apps, messaging platforms, and mobile browsers. Unlike desktop users who might tolerate slight delays for thorough analysis, mobile users expect instant results while scrolling through feeds or viewing messages. This creates a fundamental tension between detection thoroughness and user experience that shapes every architectural decision.

### Native Mobile Architectures

#### iOS Architecture with Core ML

Apple's ecosystem provides powerful on-device machine learning capabilities through Core ML, enabling sophisticated detection without network dependencies.

```swift
// DetectionEngine.swift - Core ML-based detection engine
import Foundation
import CoreML
import Vision
import AVFoundation
import Combine

@available(iOS 14.0, *)
class DetectionEngine: ObservableObject {
    // Published properties for SwiftUI binding
    @Published var detectionResults: [DetectionResult] = []
    @Published var isProcessing: Bool = false
    @Published var currentProgress: Float = 0.0
    
    // Core ML models
    private var imageDetector: VNCoreMLModel?
    private var videoDetector: VNCoreMLModel?
    private var audioDetector: MLModel?
    
    // Processing queues
    private let detectionQueue = DispatchQueue(label: "ai.detector.processing", qos: .userInitiated)
    private let resultQueue = DispatchQueue(label: "ai.detector.results", qos: .userInteractive)
    
    // Caching
    private let cache = DetectionCache()
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        loadModels()
        setupBindings()
    }
    
    private func loadModels() {
        // Load optimized Core ML models
        do {
            // Image detection model
            let imageConfig = MLModelConfiguration()
            imageConfig.computeUnits = .cpuAndNeuralEngine
            let imageModel = try DeepfakeImageDetector(configuration: imageConfig)
            self.imageDetector = try VNCoreMLModel(for: imageModel.model)
            
            // Video detection model (lighter weight)
            let videoConfig = MLModelConfiguration()
            videoConfig.computeUnits = .cpuAndGPU
            let videoModel = try VideoManipulationDetector(configuration: videoConfig)
            self.videoDetector = try VNCoreMLModel(for: videoModel.model)
            
            // Audio detection model
            self.audioDetector = try VoiceCloneDetector(configuration: imageConfig).model
            
        } catch {
            print("Model loading error: \(error)")
            // Fallback to cloud detection
        }
    }
    
    // MARK: - Image Detection
    
    func detectImage(_ image: UIImage) -> AnyPublisher<DetectionResult, Error> {
        // Check cache first
        let imageHash = image.dataHash()
        if let cached = cache.get(key: imageHash) {
            return Just(cached)
                .setFailureType(to: Error.self)
                .eraseToAnyPublisher()
        }
        
        return Future<DetectionResult, Error> { [weak self] promise in
            guard let self = self else { return }
            
            self.detectionQueue.async {
                do {
                    let result = try self.performImageDetection(image)
                    self.cache.set(key: imageHash, value: result)
                    promise(.success(result))
                } catch {
                    promise(.failure(error))
                }
            }
        }.eraseToAnyPublisher()
    }
    
    private func performImageDetection(_ image: UIImage) throws -> DetectionResult {
        guard let cgImage = image.cgImage,
              let detector = imageDetector else {
            throw DetectionError.modelNotLoaded
        }
        
        // Create Vision request
        let request = VNCoreMLRequest(model: detector) { [weak self] request, error in
            guard let results = request.results as? [VNClassificationObservation] else { return }
            
            // Process results
            let aiProbability = results.first(where: { $0.identifier == "ai_generated" })?.confidence ?? 0
            let artifacts = self?.extractArtifacts(from: results) ?? []
            
            // Additional checks for specific generation methods
            let ganScore = results.first(where: { $0.identifier == "gan" })?.confidence ?? 0
            let diffusionScore = results.first(where: { $0.identifier == "diffusion" })?.confidence ?? 0
            
            let result = DetectionResult(
                type: .image,
                isAIGenerated: aiProbability > 0.7,
                confidence: aiProbability,
                generationMethod: self?.determineMethod(gan: ganScore, diffusion: diffusionScore),
                artifacts: artifacts,
                processingTime: Date().timeIntervalSince(Date())
            )
            
            DispatchQueue.main.async {
                self?.detectionResults.append(result)
            }
        }
        
        // Configure request for optimal performance
        request.imageCropAndScaleOption = .centerCrop
        request.usesCPUOnly = false
        
        // Execute request
        let handler = VNImageRequestHandler(cgImage: cgImage)
        try handler.perform([request])
        
        return detectionResults.last!
    }
    
    // MARK: - Video Detection
    
    func detectVideo(at url: URL) -> AnyPublisher<VideoDetectionResult, Error> {
        return Future<VideoDetectionResult, Error> { [weak self] promise in
            guard let self = self else { return }
            
            self.detectionQueue.async {
                do {
                    let result = try self.performVideoDetection(url: url)
                    promise(.success(result))
                } catch {
                    promise(.failure(error))
                }
            }
        }.eraseToAnyPublisher()
    }
    
    private func performVideoDetection(url: URL) throws -> VideoDetectionResult {
        let asset = AVAsset(url: url)
        let duration = asset.duration.seconds
        
        // Sample frames at strategic intervals
        let frameCount = min(30, Int(duration * 2)) // 2 fps or 30 frames max
        let interval = duration / Double(frameCount)
        
        var frameResults: [FrameDetectionResult] = []
        let generator = AVAssetImageGenerator(asset: asset)
        generator.appliesPreferredTrackTransform = true
        generator.maximumSize = CGSize(width: 512, height: 512) // Optimize for model
        
        for i in 0..<frameCount {
            let time = CMTime(seconds: Double(i) * interval, preferredTimescale: 600)
            
            do {
                let imageRef = try generator.copyCGImage(at: time, actualTime: nil)
                let image = UIImage(cgImage: imageRef)
                
                // Quick detection per frame
                let frameResult = try performQuickImageDetection(image)
                frameResults.append(FrameDetectionResult(
                    timestamp: time.seconds,
                    confidence: frameResult.confidence,
                    artifacts: frameResult.artifacts
                ))
                
                // Update progress
                DispatchQueue.main.async {
                    self.currentProgress = Float(i + 1) / Float(frameCount)
                }
                
            } catch {
                // Skip frame on error
                continue
            }
        }
        
        // Aggregate frame results
        let overallConfidence = frameResults.map(\.confidence).reduce(0, +) / Float(frameResults.count)
        let isDeepfake = overallConfidence > 0.7
        
        // Check for temporal inconsistencies
        let temporalAnomalies = detectTemporalAnomalies(frameResults)
        
        return VideoDetectionResult(
            url: url,
            isDeepfake: isDeepfake,
            confidence: overallConfidence,
            frameResults: frameResults,
            temporalAnomalies: temporalAnomalies,
            duration: duration
        )
    }
    
    // MARK: - Audio Detection
    
    func detectAudio(at url: URL) -> AnyPublisher<AudioDetectionResult, Error> {
        return Future<AudioDetectionResult, Error> { [weak self] promise in
            guard let self = self, let model = self.audioDetector else {
                promise(.failure(DetectionError.modelNotLoaded))
                return
            }
            
            self.detectionQueue.async {
                do {
                    // Extract audio features
                    let features = try self.extractAudioFeatures(from: url)
                    
                    // Run inference
                    let prediction = try model.prediction(from: features)
                    
                    // Process results
                    let result = self.processAudioPrediction(prediction, url: url)
                    promise(.success(result))
                    
                } catch {
                    promise(.failure(error))
                }
            }
        }.eraseToAnyPublisher()
    }
    
    private func extractAudioFeatures(from url: URL) throws -> MLMultiArray {
        let file = try AVAudioFile(forReading: url)
        let format = AVAudioFormat(standardFormatWithSampleRate: 16000, channels: 1)!
        
        let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: AVAudioFrameCount(file.length))!
        try file.read(into: buffer)
        
        // Convert to mel-spectrogram
        let melSpectrogram = AudioProcessor.generateMelSpectrogram(from: buffer)
        
        // Convert to MLMultiArray
        return try MLMultiArray(melSpectrogram)
    }
}

// MARK: - SwiftUI Integration

struct ContentDetectionView: View {
    @StateObject private var detector = DetectionEngine()
    @State private var selectedImage: UIImage?
    @State private var showingResults = false
    
    var body: some View {
        NavigationView {
            VStack {
                if let image = selectedImage {
                    Image(uiImage: image)
                        .resizable()
                        .scaledToFit()
                        .overlay(DetectionOverlay(result: detector.detectionResults.last))
                }
                
                HStack {
                    Button("Select Image") {
                        // Show image picker
                    }
                    
                    Button("Detect") {
                        guard let image = selectedImage else { return }
                        
                        detector.detectImage(image)
                            .receive(on: DispatchQueue.main)
                            .sink(
                                receiveCompletion: { _ in },
                                receiveValue: { result in
                                    showingResults = true
                                }
                            )
                            .store(in: &cancellables)
                    }
                    .disabled(detector.isProcessing)
                }
                
                if detector.isProcessing {
                    ProgressView(value: detector.currentProgress)
                        .progressViewStyle(.linear)
                }
            }
            .sheet(isPresented: $showingResults) {
                DetectionResultsView(results: detector.detectionResults)
            }
        }
    }
}
```

#### Android Architecture with TensorFlow Lite

Android's implementation leverages TensorFlow Lite for efficient on-device inference with hardware acceleration.

```kotlin
// DetectionEngine.kt - TensorFlow Lite detection engine
package com.aidetector.mobile

import android.content.Context
import android.graphics.Bitmap
import android.media.MediaMetadataRetriever
import android.net.Uri
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.*
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.gpu.GpuDelegate
import org.tensorflow.lite.nnapi.NnApiDelegate
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.concurrent.Executors

class DetectionViewModel(private val context: Context) : ViewModel() {
    
    // Models
    private var imageDetector: Interpreter? = null
    private var videoDetector: Interpreter? = null
    private var audioDetector: Interpreter? = null
    
    // Delegates for hardware acceleration
    private var gpuDelegate: GpuDelegate? = null
    private var nnApiDelegate: NnApiDelegate? = null
    
    // LiveData for UI updates
    private val _detectionResults = MutableLiveData<List<DetectionResult>>()
    val detectionResults: LiveData<List<DetectionResult>> = _detectionResults
    
    private val _processingStatus = MutableLiveData<ProcessingStatus>()
    val processingStatus: LiveData<ProcessingStatus> = _processingStatus
    
    // Execution
    private val executorService = Executors.newFixedThreadPool(2)
    private val modelScope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    
    // Cache
    private val cache = LruCache<String, DetectionResult>(100)
    
    init {
        initializeModels()
    }
    
    private fun initializeModels() {
        viewModelScope.launch {
            try {
                // Initialize hardware delegates
                initializeHardwareAcceleration()
                
                // Load models
                withContext(Dispatchers.IO) {
                    imageDetector = loadModel("image_detector.tflite")
                    videoDetector = loadModel("video_detector_lite.tflite")
                    audioDetector = loadModel("audio_detector.tflite")
                }
                
                _processingStatus.value = ProcessingStatus.Ready
            } catch (e: Exception) {
                _processingStatus.value = ProcessingStatus.Error(e.message ?: "Model loading failed")
            }
        }
    }
    
    private fun initializeHardwareAcceleration() {
        try {
            // Try GPU acceleration first
            gpuDelegate = GpuDelegate()
        } catch (e: Exception) {
            // Fall back to NNAPI
            try {
                nnApiDelegate = NnApiDelegate()
            } catch (e2: Exception) {
                // Fall back to CPU
                println("Hardware acceleration not available, using CPU")
            }
        }
    }
    
    private fun loadModel(modelName: String): Interpreter {
        val modelBuffer = loadModelFile(modelName)
        
        val options = Interpreter.Options().apply {
            setNumThreads(4)
            gpuDelegate?.let { addDelegate(it) }
                ?: nnApiDelegate?.let { addDelegate(it) }
        }
        
        return Interpreter(modelBuffer, options)
    }
    
    private fun loadModelFile(modelName: String): ByteBuffer {
        val assetFileDescriptor = context.assets.openFd(modelName)
        val inputStream = assetFileDescriptor.createInputStream()
        val modelBytes = inputStream.readBytes()
        
        val buffer = ByteBuffer.allocateDirect(modelBytes.size)
        buffer.order(ByteOrder.nativeOrder())
        buffer.put(modelBytes)
        buffer.rewind()
        
        return buffer
    }
    
    // Image Detection
    fun detectImage(bitmap: Bitmap) {
        viewModelScope.launch {
            _processingStatus.value = ProcessingStatus.Processing(0f)
            
            try {
                // Check cache
                val cacheKey = bitmap.hashCode().toString()
                cache.get(cacheKey)?.let {
                    _detectionResults.value = listOf(it)
                    _processingStatus.value = ProcessingStatus.Complete
                    return@launch
                }
                
                val result = withContext(Dispatchers.Default) {
                    performImageDetection(bitmap)
                }
                
                // Cache result
                cache.put(cacheKey, result)
                
                _detectionResults.value = listOf(result)
                _processingStatus.value = ProcessingStatus.Complete
                
            } catch (e: Exception) {
                _processingStatus.value = ProcessingStatus.Error(e.message ?: "Detection failed")
            }
        }
    }
    
    private suspend fun performImageDetection(bitmap: Bitmap): DetectionResult {
        val preprocessed = preprocessImage(bitmap)
        
        // Allocate output buffer
        val output = Array(1) { FloatArray(2) } // [human, ai] probabilities
        
        // Run inference
        imageDetector?.run(preprocessed, output)
        
        val aiProbability = output[0][1]
        val isAiGenerated = aiProbability > 0.7f
        
        // Extract additional features
        val artifacts = if (isAiGenerated) {
            detectImageArtifacts(bitmap)
        } else {
            emptyList()
        }
        
        return DetectionResult(
            type = ContentType.IMAGE,
            isAiGenerated = isAiGenerated,
            confidence = aiProbability,
            artifacts = artifacts,
            metadata = mapOf(
                "resolution" to "${bitmap.width}x${bitmap.height}",
                "format" to bitmap.config.name
            )
        )
    }
    
    private fun preprocessImage(bitmap: Bitmap): ByteBuffer {
        val modelInputSize = 224
        val scaled = Bitmap.createScaledBitmap(bitmap, modelInputSize, modelInputSize, true)
        
        val buffer = ByteBuffer.allocateDirect(4 * modelInputSize * modelInputSize * 3)
        buffer.order(ByteOrder.nativeOrder())
        
        val pixels = IntArray(modelInputSize * modelInputSize)
        scaled.getPixels(pixels, 0, modelInputSize, 0, 0, modelInputSize, modelInputSize)
        
        // Normalize pixels
        for (pixel in pixels) {
            val r = ((pixel shr 16 and 0xFF) - 127.5f) / 127.5f
            val g = ((pixel shr 8 and 0xFF) - 127.5f) / 127.5f
            val b = ((pixel and 0xFF) - 127.5f) / 127.5f
            
            buffer.putFloat(r)
            buffer.putFloat(g)
            buffer.putFloat(b)
        }
        
        buffer.rewind()
        return buffer
    }
    
    // Video Detection
    fun detectVideo(uri: Uri) {
        viewModelScope.launch {
            _processingStatus.value = ProcessingStatus.Processing(0f)
            
            try {
                val results = withContext(Dispatchers.IO) {
                    performVideoDetection(uri)
                }
                
                _detectionResults.value = results
                _processingStatus.value = ProcessingStatus.Complete
                
            } catch (e: Exception) {
                _processingStatus.value = ProcessingStatus.Error(e.message ?: "Video detection failed")
            }
        }
    }
    
    private suspend fun performVideoDetection(uri: Uri): List<DetectionResult> = coroutineScope {
        val retriever = MediaMetadataRetriever()
        retriever.setDataSource(context, uri)
        
        val duration = retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_DURATION)?.toLong() ?: 0
        val frameResults = mutableListOf<Deferred<FrameResult>>()
        
        // Sample frames
        val frameCount = minOf(30, (duration / 1000).toInt()) // Max 30 frames
        val interval = duration * 1000 / frameCount // microseconds
        
        for (i in 0 until frameCount) {
            val timestamp = i * interval
            
            frameResults.add(async {
                val frame = retriever.getFrameAtTime(timestamp)
                if (frame != null) {
                    val detection = performQuickImageDetection(frame)
                    FrameResult(timestamp, detection)
                } else {
                    FrameResult(timestamp, null)
                }
            })
            
            // Update progress
            _processingStatus.postValue(ProcessingStatus.Processing((i + 1).toFloat() / frameCount))
        }
        
        // Wait for all frames
        val frames = frameResults.awaitAll()
        
        // Aggregate results
        val validFrames = frames.mapNotNull { it.detection }
        val avgConfidence = validFrames.map { it.confidence }.average().toFloat()
        
        // Detect temporal inconsistencies
        val temporalAnomalies = detectTemporalAnomalies(frames)
        
        retriever.release()
        
        listOf(
            DetectionResult(
                type = ContentType.VIDEO,
                isAiGenerated = avgConfidence > 0.7f,
                confidence = avgConfidence,
                artifacts = temporalAnomalies,
                metadata = mapOf(
                    "duration" to "${duration / 1000}s",
                    "frames_analyzed" to frameCount.toString()
                )
            )
        )
    }
    
    // Cleanup
    override fun onCleared() {
        super.onCleared()
        executorService.shutdown()
        modelScope.cancel()
        
        imageDetector?.close()
        videoDetector?.close()
        audioDetector?.close()
        
        gpuDelegate?.close()
        nnApiDelegate?.close()
    }
}

// UI Integration
@Composable
fun DetectionScreen(viewModel: DetectionViewModel = viewModel()) {
    val results by viewModel.detectionResults.observeAsState(emptyList())
    val status by viewModel.processingStatus.observeAsState(ProcessingStatus.Ready)
    
    var selectedImageUri by remember { mutableStateOf<Uri?>(null) }
    
    val launcher = rememberLauncherForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri ->
        selectedImageUri = uri
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        selectedImageUri?.let { uri ->
            AsyncImage(
                model = uri,
                contentDescription = "Selected image",
                modifier = Modifier
                    .fillMaxWidth()
                    .height(300.dp)
            )
        }
        
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            Button(
                onClick = { launcher.launch("image/*") }
            ) {
                Text("Select Image")
            }
            
            Button(
                onClick = {
                    selectedImageUri?.let { uri ->
                        val bitmap = MediaStore.Images.Media.getBitmap(
                            context.contentResolver, uri
                        )
                        viewModel.detectImage(bitmap)
                    }
                },
                enabled = selectedImageUri != null && status is ProcessingStatus.Ready
            ) {
                Text("Detect")
            }
        }
        
        when (status) {
            is ProcessingStatus.Processing -> {
                LinearProgressIndicator(
                    progress = status.progress,
                    modifier = Modifier.fillMaxWidth()
                )
            }
            is ProcessingStatus.Error -> {
                Text(
                    text = "Error: ${status.message}",
                    color = MaterialTheme.colors.error
                )
            }
            else -> {}
        }
        
        LazyColumn {
            items(results) { result ->
                DetectionResultCard(result)
            }
        }
    }
}
```

### Cross-Platform Frameworks

#### React Native with Native Modules

For teams requiring cross-platform deployment, React Native with custom native modules provides a balance between code reuse and platform-specific optimization.

```javascript
// DetectionBridge.js - React Native bridge to native detection
import { NativeModules, NativeEventEmitter, Platform } from 'react-native';

const { AIDetector } = NativeModules;
const detectorEvents = new NativeEventEmitter(AIDetector);

class DetectionBridge {
  constructor() {
    this.listeners = new Map();
    this.initializeNativeModule();
  }
  
  async initializeNativeModule() {
    try {
      const result = await AIDetector.initialize({
        enableGPU: true,
        cacheSize: 100,
        modelQuality: 'balanced' // 'fast', 'balanced', 'accurate'
      });
      
      console.log('AI Detector initialized:', result);
    } catch (error) {
      console.error('Failed to initialize AI Detector:', error);
    }
  }
  
  async detectImage(imagePath) {
    try {
      // Platform-specific preprocessing
      const processedPath = Platform.select({
        ios: imagePath.replace('file://', ''),
        android: imagePath
      });
      
      const result = await AIDetector.detectImage(processedPath);
      
      return {
        isAIGenerated: result.isAIGenerated,
        confidence: result.confidence,
        method: result.generationMethod,
        artifacts: result.artifacts || [],
        processingTime: result.processingTime
      };
    } catch (error) {
      console.error('Image detection failed:', error);
      throw error;
    }
  }
  
  async detectVideo(videoPath, options = {}) {
    const taskId = Date.now().toString();
    
    return new Promise((resolve, reject) => {
      // Listen for progress updates
      const progressListener = detectorEvents.addListener(
        'VideoDetectionProgress',
        (event) => {
          if (event.taskId === taskId) {
            options.onProgress?.(event.progress);
          }
        }
      );
      
      // Listen for completion
      const completionListener = detectorEvents.addListener(
        'VideoDetectionComplete',
        (event) => {
          if (event.taskId === taskId) {
            progressListener.remove();
            completionListener.remove();
            
            if (event.error) {
              reject(new Error(event.error));
            } else {
              resolve(event.result);
            }
          }
        }
      );
      
      // Start detection
      AIDetector.detectVideo({
        path: videoPath,
        taskId,
        frameSkip: options.frameSkip || 5,
        maxFrames: options.maxFrames || 30
      });
    });
  }
  
  async detectRealtimeCamera() {
    // Real-time camera detection for live streaming
    return new Promise((resolve, reject) => {
      const listener = detectorEvents.addListener(
        'RealtimeDetection',
        (event) => {
          if (event.type === 'frame') {
            // Process frame result
            this.processRealtimeFrame(event.result);
          } else if (event.type === 'error') {
            reject(new Error(event.error));
          }
        }
      );
      
      AIDetector.startRealtimeDetection({
        cameraPosition: 'front',
        detectionInterval: 500, // ms between detections
        confidenceThreshold: 0.7
      });
      
      // Return stop function
      resolve(() => {
        AIDetector.stopRealtimeDetection();
        listener.remove();
      });
    });
  }
}

export default new DetectionBridge();
```

This chapter continues with sections on offline capabilities, model optimization, and privacy-preserving architectures...