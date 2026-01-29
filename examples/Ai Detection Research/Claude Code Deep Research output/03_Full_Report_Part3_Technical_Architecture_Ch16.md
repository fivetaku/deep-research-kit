## Chapter 16: Browser Extension Development

### The Browser as a Detection Platform

Browser extensions have emerged as a critical frontline defense against AI-generated content, offering real-time detection capabilities directly where users consume media. Unlike server-side solutions, browser extensions provide immediate feedback, preserve user privacy by processing content locally, and integrate seamlessly into existing workflows. The challenge lies in balancing detection accuracy with performance constraints, as extensions must operate within strict memory and CPU limits while maintaining responsive user experiences.

The browser extension ecosystem spans millions of users across Chrome, Firefox, Safari, and Edge, making it one of the most impactful distribution channels for detection technology. However, developing effective detection extensions requires navigating complex technical constraints, evolving web standards, and platform-specific limitations that vary significantly across browsers.

### Architecture Fundamentals

#### Manifest V3 Compliance

Modern browser extensions must comply with Manifest V3 specifications, which introduce significant architectural changes focused on security and performance.

```json
// manifest.json - Chrome/Edge Manifest V3
{
  "manifest_version": 3,
  "name": "AI Content Detector Pro",
  "version": "2.0.0",
  "description": "Real-time detection of AI-generated content across the web",
  
  "permissions": [
    "activeTab",
    "storage",
    "contextMenus",
    "scripting"
  ],
  
  "host_permissions": [
    "https://*/*",
    "http://*/*"
  ],
  
  "background": {
    "service_worker": "background.js",
    "type": "module"
  },
  
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content/injector.js"],
      "css": ["content/overlay.css"],
      "run_at": "document_idle"
    }
  ],
  
  "action": {
    "default_popup": "popup/index.html",
    "default_icon": {
      "16": "icons/icon-16.png",
      "32": "icons/icon-32.png",
      "48": "icons/icon-48.png",
      "128": "icons/icon-128.png"
    }
  },
  
  "web_accessible_resources": [
    {
      "resources": [
        "wasm/detector.wasm",
        "models/*",
        "content/detection-ui.html"
      ],
      "matches": ["<all_urls>"]
    }
  ],
  
  "content_security_policy": {
    "extension_pages": "script-src 'self' 'wasm-unsafe-eval'; object-src 'self'"
  }
}
```

#### Service Worker Architecture

The shift from persistent background pages to service workers requires careful state management and efficient resource utilization.

```javascript
// background.js - Service Worker implementation
import { DetectionEngine } from './detection/engine.js';
import { CacheManager } from './utils/cache.js';
import { APIClient } from './api/client.js';

// Initialize on install
self.addEventListener('install', (event) => {
  event.waitUntil(
    (async () => {
      // Preload critical resources
      const cache = await caches.open('detector-v1');
      await cache.addAll([
        '/wasm/detector.wasm',
        '/models/image-classifier.onnx',
        '/models/text-analyzer.json'
      ]);
      
      // Initialize detection engine
      await DetectionEngine.initialize();
    })()
  );
});

// Handle detection requests from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'DETECT_CONTENT') {
    handleDetectionRequest(request, sender)
      .then(sendResponse)
      .catch(error => sendResponse({ error: error.message }));
    return true; // Keep channel open for async response
  }
});

async function handleDetectionRequest(request, sender) {
  const { contentType, data, options } = request;
  
  // Check cache first
  const cacheKey = await CacheManager.generateKey(data);
  const cached = await CacheManager.get(cacheKey);
  
  if (cached && !options.forceRefresh) {
    return { source: 'cache', ...cached };
  }
  
  // Perform detection based on content type
  let result;
  switch (contentType) {
    case 'image':
      result = await detectImage(data, options);
      break;
    case 'video':
      result = await detectVideo(data, options);
      break;
    case 'text':
      result = await detectText(data, options);
      break;
    case 'audio':
      result = await detectAudio(data, options);
      break;
    default:
      throw new Error(`Unsupported content type: ${contentType}`);
  }
  
  // Cache result
  await CacheManager.set(cacheKey, result, options.cacheDuration || 3600);
  
  // Update badge if configured
  if (options.updateBadge) {
    updateBadge(sender.tab.id, result);
  }
  
  return { source: 'fresh', ...result };
}

// Badge management
function updateBadge(tabId, result) {
  const { confidence, isAiGenerated } = result;
  
  if (isAiGenerated) {
    chrome.action.setBadgeText({ text: 'AI', tabId });
    chrome.action.setBadgeBackgroundColor({ 
      color: confidence > 0.8 ? '#FF0000' : '#FFA500',
      tabId 
    });
  } else {
    chrome.action.setBadgeText({ text: '', tabId });
  }
}
```

### Content Script Implementation

Content scripts interact directly with web pages, requiring careful isolation and efficient communication patterns.

```javascript
// content/injector.js - Main content script
(function() {
  'use strict';
  
  // Prevent multiple injections
  if (window.__aiDetectorInjected) return;
  window.__aiDetectorInjected = true;
  
  class ContentDetector {
    constructor() {
      this.observer = null;
      this.detectedElements = new WeakMap();
      this.pendingDetections = new Map();
      this.uiController = new UIController();
      
      this.init();
    }
    
    init() {
      // Start observing DOM changes
      this.startObserver();
      
      // Scan existing content
      this.scanPage();
      
      // Listen for user interactions
      this.setupEventListeners();
      
      // Handle dynamic content (infinite scroll, AJAX)
      this.interceptNetworkRequests();
    }
    
    startObserver() {
      this.observer = new MutationObserver((mutations) => {
        const addedElements = new Set();
        
        mutations.forEach(mutation => {
          mutation.addedNodes.forEach(node => {
            if (node.nodeType === Node.ELEMENT_NODE) {
              this.collectDetectableElements(node, addedElements);
            }
          });
        });
        
        if (addedElements.size > 0) {
          this.processElements(Array.from(addedElements));
        }
      });
      
      this.observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['src', 'href']
      });
    }
    
    collectDetectableElements(root, collection) {
      // Images
      const images = root.querySelectorAll('img[src], picture source');
      images.forEach(img => collection.add(img));
      
      // Videos
      const videos = root.querySelectorAll('video[src], video source');
      videos.forEach(video => collection.add(video));
      
      // Audio elements
      const audios = root.querySelectorAll('audio[src], audio source');
      audios.forEach(audio => collection.add(audio));
      
      // Text content (articles, posts)
      const textContainers = root.querySelectorAll(
        'article, [role="article"], .post-content, .comment-body'
      );
      textContainers.forEach(container => {
        if (container.textContent.trim().length > 100) {
          collection.add(container);
        }
      });
    }
    
    async processElements(elements) {
      const batch = [];
      
      for (const element of elements) {
        // Skip if already processed
        if (this.detectedElements.has(element)) continue;
        
        const detection = this.prepareDetection(element);
        if (detection) {
          batch.push(detection);
          this.detectedElements.set(element, { status: 'pending' });
        }
      }
      
      if (batch.length === 0) return;
      
      // Send batch to service worker
      const results = await chrome.runtime.sendMessage({
        type: 'DETECT_CONTENT_BATCH',
        detections: batch
      });
      
      // Apply results to UI
      results.forEach((result, index) => {
        const element = batch[index].element;
        this.detectedElements.set(element, result);
        this.uiController.applyDetectionUI(element, result);
      });
    }
    
    prepareDetection(element) {
      const tagName = element.tagName.toLowerCase();
      
      switch (tagName) {
        case 'img':
          return this.prepareImageDetection(element);
        case 'video':
          return this.prepareVideoDetection(element);
        case 'audio':
          return this.prepareAudioDetection(element);
        default:
          if (element.textContent.trim().length > 100) {
            return this.prepareTextDetection(element);
          }
      }
      
      return null;
    }
    
    prepareImageDetection(img) {
      // Skip small images (likely icons)
      if (img.width < 100 || img.height < 100) return null;
      
      // Skip data URLs for performance
      if (img.src.startsWith('data:')) return null;
      
      return {
        element: img,
        type: 'image',
        url: img.src,
        metadata: {
          width: img.naturalWidth,
          height: img.naturalHeight,
          alt: img.alt
        }
      };
    }
    
    interceptNetworkRequests() {
      // Intercept fetch requests to detect dynamically loaded content
      const originalFetch = window.fetch;
      window.fetch = async (...args) => {
        const response = await originalFetch(...args);
        
        // Clone response for analysis
        const clone = response.clone();
        const contentType = clone.headers.get('content-type');
        
        if (contentType && contentType.includes('image')) {
          // Queue for detection after insertion into DOM
          setTimeout(() => this.scanPage(), 100);
        }
        
        return response;
      };
    }
  }
  
  // UI Controller for visual feedback
  class UIController {
    constructor() {
      this.overlayTemplate = this.createOverlayTemplate();
      this.styles = this.injectStyles();
    }
    
    createOverlayTemplate() {
      const template = document.createElement('template');
      template.innerHTML = `
        <div class="ai-detector-overlay">
          <div class="ai-detector-badge">
            <span class="ai-detector-icon"></span>
            <span class="ai-detector-label"></span>
            <span class="ai-detector-confidence"></span>
          </div>
          <div class="ai-detector-details">
            <div class="ai-detector-evidence"></div>
            <button class="ai-detector-report">Report</button>
          </div>
        </div>
      `;
      return template;
    }
    
    applyDetectionUI(element, detection) {
      if (!detection.isAiGenerated && detection.confidence < 0.7) {
        return; // Don't clutter UI with low-confidence human content
      }
      
      const wrapper = document.createElement('div');
      wrapper.className = 'ai-detector-wrapper';
      wrapper.style.position = 'relative';
      wrapper.style.display = 'inline-block';
      
      // Clone original element
      const clone = element.cloneNode(true);
      element.parentNode.replaceChild(wrapper, element);
      wrapper.appendChild(clone);
      
      // Add overlay
      const overlay = this.overlayTemplate.content.cloneNode(true);
      const badge = overlay.querySelector('.ai-detector-badge');
      const label = overlay.querySelector('.ai-detector-label');
      const confidence = overlay.querySelector('.ai-detector-confidence');
      
      // Update content
      label.textContent = detection.isAiGenerated ? 'AI Generated' : 'Human Created';
      confidence.textContent = `${Math.round(detection.confidence * 100)}%`;
      
      // Style based on detection
      badge.className += detection.isAiGenerated ? 
        ' ai-detected' : ' human-verified';
      
      wrapper.appendChild(overlay);
      
      // Add hover interactions
      this.setupInteractions(wrapper, detection);
    }
    
    setupInteractions(wrapper, detection) {
      const badge = wrapper.querySelector('.ai-detector-badge');
      const details = wrapper.querySelector('.ai-detector-details');
      
      badge.addEventListener('click', (e) => {
        e.stopPropagation();
        details.classList.toggle('visible');
        
        // Load detailed evidence
        if (details.classList.contains('visible')) {
          this.loadDetailedEvidence(details, detection);
        }
      });
      
      // Report button
      const reportBtn = wrapper.querySelector('.ai-detector-report');
      reportBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.reportDetection(detection);
      });
    }
    
    injectStyles() {
      const style = document.createElement('style');
      style.textContent = `
        .ai-detector-wrapper {
          position: relative !important;
          display: inline-block !important;
        }
        
        .ai-detector-overlay {
          position: absolute;
          top: 10px;
          right: 10px;
          z-index: 10000;
          pointer-events: none;
        }
        
        .ai-detector-badge {
          background: rgba(0, 0, 0, 0.8);
          color: white;
          padding: 6px 12px;
          border-radius: 20px;
          font-size: 12px;
          font-family: -apple-system, system-ui, sans-serif;
          display: flex;
          align-items: center;
          gap: 6px;
          cursor: pointer;
          pointer-events: auto;
          transition: all 0.2s ease;
        }
        
        .ai-detector-badge:hover {
          transform: scale(1.05);
          background: rgba(0, 0, 0, 0.9);
        }
        
        .ai-detector-badge.ai-detected {
          background: rgba(220, 38, 38, 0.9);
        }
        
        .ai-detector-badge.human-verified {
          background: rgba(34, 197, 94, 0.9);
        }
        
        .ai-detector-icon::before {
          content: "🤖";
          font-size: 14px;
        }
        
        .ai-detector-badge.human-verified .ai-detector-icon::before {
          content: "✓";
        }
        
        .ai-detector-details {
          display: none;
          position: absolute;
          top: 40px;
          right: 0;
          background: white;
          border: 1px solid #ddd;
          border-radius: 8px;
          padding: 16px;
          width: 300px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
          pointer-events: auto;
        }
        
        .ai-detector-details.visible {
          display: block;
        }
        
        .ai-detector-evidence {
          margin-bottom: 12px;
          font-size: 14px;
          line-height: 1.5;
          color: #333;
        }
        
        .ai-detector-report {
          background: #3b82f6;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
        }
        
        .ai-detector-report:hover {
          background: #2563eb;
        }
      `;
      document.head.appendChild(style);
      return style;
    }
  }
  
  // Initialize detector
  const detector = new ContentDetector();
})();
```

### WebAssembly Integration

For performance-critical detection algorithms, WebAssembly provides near-native execution speed within the browser.

```rust
// src/detector.rs - Rust code compiled to WASM
use wasm_bindgen::prelude::*;
use web_sys::console;

#[wasm_bindgen]
pub struct ImageDetector {
    model: Model,
    threshold: f32,
}

#[wasm_bindgen]
impl ImageDetector {
    #[wasm_bindgen(constructor)]
    pub fn new(model_bytes: &[u8], threshold: f32) -> Result<ImageDetector, JsValue> {
        console::log_1(&"Initializing WASM detector".into());
        
        let model = Model::load(model_bytes)
            .map_err(|e| JsValue::from_str(&format!("Model load error: {}", e)))?;
        
        Ok(ImageDetector { model, threshold })
    }
    
    #[wasm_bindgen]
    pub fn detect(&self, image_data: &[u8], width: u32, height: u32) -> DetectionResult {
        // Preprocess image
        let preprocessed = self.preprocess_image(image_data, width, height);
        
        // Run inference
        let features = self.model.extract_features(&preprocessed);
        let score = self.model.predict(&features);
        
        // Analyze patterns
        let artifacts = self.detect_artifacts(&preprocessed);
        
        DetectionResult {
            is_ai_generated: score > self.threshold,
            confidence: score,
            artifacts: artifacts.into_iter().map(|a| a.to_string()).collect(),
            processing_time_ms: 0, // Would use performance.now() in real impl
        }
    }
    
    fn preprocess_image(&self, data: &[u8], width: u32, height: u32) -> ProcessedImage {
        // Convert to normalized tensor
        let mut tensor = vec![0.0f32; (width * height * 3) as usize];
        
        for i in 0..data.len() / 4 {
            let r = data[i * 4] as f32 / 255.0;
            let g = data[i * 4 + 1] as f32 / 255.0;
            let b = data[i * 4 + 2] as f32 / 255.0;
            
            tensor[i * 3] = (r - 0.485) / 0.229;
            tensor[i * 3 + 1] = (g - 0.456) / 0.224;
            tensor[i * 3 + 2] = (b - 0.406) / 0.225;
        }
        
        ProcessedImage { tensor, width, height }
    }
    
    fn detect_artifacts(&self, image: &ProcessedImage) -> Vec<Artifact> {
        let mut artifacts = Vec::new();
        
        // Check for GAN fingerprints
        if self.detect_gan_artifacts(image) {
            artifacts.push(Artifact::GanFingerprint);
        }
        
        // Check for diffusion patterns
        if self.detect_diffusion_artifacts(image) {
            artifacts.push(Artifact::DiffusionNoise);
        }
        
        // Check for frequency anomalies
        if self.detect_frequency_anomalies(image) {
            artifacts.push(Artifact::FrequencyAnomaly);
        }
        
        artifacts
    }
}

#[wasm_bindgen]
pub struct DetectionResult {
    pub is_ai_generated: bool,
    pub confidence: f32,
    pub artifacts: Vec<String>,
    pub processing_time_ms: u32,
}
```

```javascript
// wasm/loader.js - WASM module loader
export class WASMDetector {
  constructor() {
    this.module = null;
    this.detector = null;
  }
  
  async initialize() {
    // Load WASM module
    const wasmBytes = await fetch(
      chrome.runtime.getURL('wasm/detector.wasm')
    ).then(r => r.arrayBuffer());
    
    // Initialize module
    this.module = await import('./detector.js');
    await this.module.default(wasmBytes);
    
    // Load model
    const modelBytes = await fetch(
      chrome.runtime.getURL('models/image_detector.bin')
    ).then(r => r.arrayBuffer());
    
    this.detector = new this.module.ImageDetector(
      new Uint8Array(modelBytes),
      0.7 // threshold
    );
  }
  
  async detectImage(imageElement) {
    // Extract image data
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = imageElement.naturalWidth;
    canvas.height = imageElement.naturalHeight;
    ctx.drawImage(imageElement, 0, 0);
    
    const imageData = ctx.getImageData(
      0, 0, canvas.width, canvas.height
    );
    
    // Run detection in WASM
    const result = this.detector.detect(
      imageData.data,
      canvas.width,
      canvas.height
    );
    
    return {
      isAiGenerated: result.is_ai_generated,
      confidence: result.confidence,
      artifacts: result.artifacts,
      processingTime: result.processing_time_ms
    };
  }
}
```

This chapter continues with sections on cross-browser compatibility, performance optimization, and user privacy considerations...