# AI Detection API Integration Code Examples

This document provides production-ready code examples for integrating various AI detection APIs across multiple programming languages and frameworks.

## Table of Contents

1. [Quick Start Examples](#quick-start-examples)
2. [Production-Ready Implementations](#production-ready-implementations)
3. [Framework-Specific Integrations](#framework-specific-integrations)
4. [Error Handling and Resilience](#error-handling-and-resilience)
5. [Testing and Validation](#testing-and-validation)

## Quick Start Examples

### Python - Basic Detection

```python
# install: pip install requests aiohttp

import requests
import asyncio
import aiohttp
from typing import Dict, Optional

class QuickAIDetector:
    """Simple AI detection client for quick integration"""
    
    def __init__(self, api_key: str, provider: str = "hive"):
        self.api_key = api_key
        self.providers = {
            "hive": "https://api.thehive.ai/api/v2",
            "azure": "https://your-resource.cognitiveservices.azure.com",
            "aws": "https://rekognition.us-east-1.amazonaws.com"
        }
        self.base_url = self.providers.get(provider, self.providers["hive"])
    
    def detect_ai_text(self, text: str) -> Dict:
        """Detect AI-generated text"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        response = requests.post(
            f"{self.base_url}/ai-generated-content/text",
            json={"text": text},
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}", "message": response.text}
    
    async def detect_ai_image_async(self, image_url: str) -> Dict:
        """Async detection for images"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/ai-generated-content/image",
                json={"url": image_url},
                headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"API error: {response.status}"}

# Usage example
detector = QuickAIDetector(api_key="your-api-key")

# Sync text detection
result = detector.detect_ai_text("This is some text to check")
print(f"AI Generated: {result.get('ai_generated', {}).get('confidence', 0):.2%}")

# Async image detection
async def check_image():
    result = await detector.detect_ai_image_async("https://example.com/image.jpg")
    print(f"Image AI Score: {result}")

# Run async function
asyncio.run(check_image())
```

### JavaScript/Node.js - Basic Detection

```javascript
// install: npm install axios node-fetch

const axios = require('axios');

class AIDetectionClient {
    constructor(apiKey, provider = 'hive') {
        this.apiKey = apiKey;
        this.providers = {
            hive: 'https://api.thehive.ai/api/v2',
            azure: 'https://your-resource.cognitiveservices.azure.com',
            google: 'https://vision.googleapis.com/v1'
        };
        this.baseUrl = this.providers[provider];
    }

    async detectText(text) {
        try {
            const response = await axios.post(
                `${this.baseUrl}/ai-generated-content/text`,
                { text },
                {
                    headers: {
                        'Authorization': `Bearer ${this.apiKey}`,
                        'Content-Type': 'application/json'
                    }
                }
            );
            return response.data;
        } catch (error) {
            console.error('Detection error:', error.message);
            return { error: error.message };
        }
    }

    async detectImage(imageUrl) {
        try {
            const response = await axios.post(
                `${this.baseUrl}/ai-generated-content/image`,
                { url: imageUrl },
                {
                    headers: {
                        'Authorization': `Bearer ${this.apiKey}`,
                        'Content-Type': 'application/json'
                    }
                }
            );
            return response.data;
        } catch (error) {
            console.error('Detection error:', error.message);
            return { error: error.message };
        }
    }

    async detectBatch(items) {
        const promises = items.map(item => {
            if (item.type === 'text') {
                return this.detectText(item.content);
            } else if (item.type === 'image') {
                return this.detectImage(item.content);
            }
        });
        
        return Promise.all(promises);
    }
}

// Usage
const detector = new AIDetectionClient('your-api-key');

// Single detection
detector.detectText('Check this text for AI generation')
    .then(result => {
        console.log('AI confidence:', result.ai_generated?.confidence || 0);
    });

// Batch detection
const items = [
    { type: 'text', content: 'Some text here' },
    { type: 'image', content: 'https://example.com/image.jpg' }
];

detector.detectBatch(items)
    .then(results => {
        results.forEach((result, index) => {
            console.log(`Item ${index}:`, result);
        });
    });
```

### Java - Basic Detection

```java
// Maven dependency:
// <dependency>
//     <groupId>com.squareup.okhttp3</groupId>
//     <artifactId>okhttp</artifactId>
//     <version>4.11.0</version>
// </dependency>

import okhttp3.*;
import com.google.gson.Gson;
import java.io.IOException;
import java.util.Map;
import java.util.HashMap;

public class AIDetectionClient {
    private final String apiKey;
    private final String baseUrl;
    private final OkHttpClient client;
    private final Gson gson;
    
    public AIDetectionClient(String apiKey, String provider) {
        this.apiKey = apiKey;
        this.client = new OkHttpClient();
        this.gson = new Gson();
        
        Map<String, String> providers = new HashMap<>();
        providers.put("hive", "https://api.thehive.ai/api/v2");
        providers.put("azure", "https://your-resource.cognitiveservices.azure.com");
        
        this.baseUrl = providers.getOrDefault(provider, providers.get("hive"));
    }
    
    public DetectionResult detectText(String text) throws IOException {
        Map<String, String> payload = new HashMap<>();
        payload.put("text", text);
        
        RequestBody body = RequestBody.create(
            gson.toJson(payload),
            MediaType.parse("application/json")
        );
        
        Request request = new Request.Builder()
            .url(baseUrl + "/ai-generated-content/text")
            .header("Authorization", "Bearer " + apiKey)
            .post(body)
            .build();
        
        try (Response response = client.newCall(request).execute()) {
            if (response.isSuccessful()) {
                String responseBody = response.body().string();
                return gson.fromJson(responseBody, DetectionResult.class);
            } else {
                throw new IOException("API error: " + response.code());
            }
        }
    }
    
    public static class DetectionResult {
        public AIGenerated ai_generated;
        public double overall_confidence;
        
        public static class AIGenerated {
            public boolean detected;
            public double confidence;
        }
    }
    
    // Usage example
    public static void main(String[] args) {
        AIDetectionClient client = new AIDetectionClient("your-api-key", "hive");
        
        try {
            DetectionResult result = client.detectText("Text to check");
            System.out.printf("AI Detected: %b (%.2f%% confidence)%n",
                result.ai_generated.detected,
                result.ai_generated.confidence * 100
            );
        } catch (IOException e) {
            System.err.println("Error: " + e.getMessage());
        }
    }
}
```

### Go - Basic Detection

```go
// install: go get -u github.com/go-resty/resty/v2

package main

import (
    "fmt"
    "log"
    "github.com/go-resty/resty/v2"
)

type AIDetector struct {
    client  *resty.Client
    apiKey  string
    baseURL string
}

type DetectionRequest struct {
    Text string `json:"text,omitempty"`
    URL  string `json:"url,omitempty"`
}

type DetectionResponse struct {
    AIGenerated struct {
        Detected   bool    `json:"detected"`
        Confidence float64 `json:"confidence"`
    } `json:"ai_generated"`
    Error string `json:"error,omitempty"`
}

func NewAIDetector(apiKey, provider string) *AIDetector {
    providers := map[string]string{
        "hive":  "https://api.thehive.ai/api/v2",
        "azure": "https://your-resource.cognitiveservices.azure.com",
    }
    
    baseURL, exists := providers[provider]
    if !exists {
        baseURL = providers["hive"]
    }
    
    client := resty.New()
    client.SetHeader("Authorization", "Bearer "+apiKey)
    client.SetHeader("Content-Type", "application/json")
    
    return &AIDetector{
        client:  client,
        apiKey:  apiKey,
        baseURL: baseURL,
    }
}

func (d *AIDetector) DetectText(text string) (*DetectionResponse, error) {
    var result DetectionResponse
    
    resp, err := d.client.R().
        SetBody(DetectionRequest{Text: text}).
        SetResult(&result).
        Post(d.baseURL + "/ai-generated-content/text")
    
    if err != nil {
        return nil, err
    }
    
    if resp.StatusCode() != 200 {
        return nil, fmt.Errorf("API error: %d", resp.StatusCode())
    }
    
    return &result, nil
}

func (d *AIDetector) DetectImage(imageURL string) (*DetectionResponse, error) {
    var result DetectionResponse
    
    resp, err := d.client.R().
        SetBody(DetectionRequest{URL: imageURL}).
        SetResult(&result).
        Post(d.baseURL + "/ai-generated-content/image")
    
    if err != nil {
        return nil, err
    }
    
    if resp.StatusCode() != 200 {
        return nil, fmt.Errorf("API error: %d", resp.StatusCode())
    }
    
    return &result, nil
}

// Usage
func main() {
    detector := NewAIDetector("your-api-key", "hive")
    
    // Detect text
    result, err := detector.DetectText("Some text to check")
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Printf("AI Detected: %v (%.2f%% confidence)\n",
        result.AIGenerated.Detected,
        result.AIGenerated.Confidence*100)
}
```

## Production-Ready Implementations

### Python - Enterprise Client with Full Features

```python
import asyncio
import time
from typing import Dict, List, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
import aiohttp
import backoff
from circuitbreaker import circuit
import logging
from functools import lru_cache
import hashlib
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Provider(Enum):
    HIVE = "hive"
    AZURE = "azure"
    AWS = "aws"
    GOOGLE = "google"
    REALITY_DEFENDER = "reality_defender"
    SENSITY = "sensity"

@dataclass
class DetectionConfig:
    api_key: str
    provider: Provider
    timeout: int = 30
    max_retries: int = 3
    cache_ttl: int = 3600
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60

@dataclass
class DetectionResult:
    detected: bool
    confidence: float
    provider: str
    details: Dict
    timestamp: float
    cached: bool = False

class AIDetectionService:
    """Production-ready AI detection service with caching, circuit breaker, and retry logic"""
    
    PROVIDER_ENDPOINTS = {
        Provider.HIVE: {
            "base": "https://api.thehive.ai/api/v2",
            "text": "/ai-generated-content/text",
            "image": "/ai-generated-content/image",
            "video": "/deepfake/video"
        },
        Provider.AZURE: {
            "base": "https://{resource}.cognitiveservices.azure.com",
            "text": "/contentsafety/text:analyze",
            "image": "/contentsafety/image:analyze"
        },
        Provider.AWS: {
            "base": "https://rekognition.{region}.amazonaws.com",
            "image": "/detect-moderation-labels"
        }
    }
    
    def __init__(self, configs: List[DetectionConfig]):
        self.configs = {config.provider: config for config in configs}
        self.sessions = {}
        self.cache = {}
        self._init_sessions()
    
    def _init_sessions(self):
        """Initialize aiohttp sessions with proper timeouts"""
        for provider, config in self.configs.items():
            timeout = aiohttp.ClientTimeout(total=config.timeout)
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            self.sessions[provider] = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            )
    
    async def close(self):
        """Clean up sessions"""
        for session in self.sessions.values():
            await session.close()
    
    def _get_cache_key(self, content: str, provider: Provider, content_type: str) -> str:
        """Generate cache key from content"""
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        return f"{provider.value}:{content_type}:{content_hash}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[DetectionResult]:
        """Get result from cache if not expired"""
        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.configs[result.provider].cache_ttl:
                result.cached = True
                return result
        return None
    
    def _save_to_cache(self, cache_key: str, result: DetectionResult):
        """Save result to cache"""
        self.cache[cache_key] = (result, time.time())
    
    @circuit(failure_threshold=5, recovery_timeout=60)
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3
    )
    async def _make_request(
        self, 
        provider: Provider, 
        endpoint: str, 
        payload: Dict
    ) -> Dict:
        """Make API request with circuit breaker and retry logic"""
        config = self.configs[provider]
        session = self.sessions[provider]
        
        headers = self._get_headers(provider, config)
        url = self._build_url(provider, endpoint)
        
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise aiohttp.ClientError(
                    f"API error {response.status}: {error_text}"
                )
    
    def _get_headers(self, provider: Provider, config: DetectionConfig) -> Dict:
        """Get provider-specific headers"""
        if provider == Provider.HIVE:
            return {"Authorization": f"Bearer {config.api_key}"}
        elif provider == Provider.AZURE:
            return {"Ocp-Apim-Subscription-Key": config.api_key}
        elif provider == Provider.AWS:
            # AWS uses signature v4, simplified here
            return {"Authorization": f"AWS4-HMAC-SHA256 {config.api_key}"}
        return {}
    
    def _build_url(self, provider: Provider, endpoint_key: str) -> str:
        """Build provider-specific URL"""
        endpoints = self.PROVIDER_ENDPOINTS[provider]
        base_url = endpoints["base"]
        
        # Handle provider-specific URL formatting
        if provider == Provider.AZURE:
            # Replace {resource} placeholder
            base_url = base_url.replace("{resource}", "your-resource")
        elif provider == Provider.AWS:
            # Replace {region} placeholder
            base_url = base_url.replace("{region}", "us-east-1")
        
        return base_url + endpoints.get(endpoint_key, "")
    
    async def detect_text(
        self, 
        text: str, 
        providers: Optional[List[Provider]] = None
    ) -> List[DetectionResult]:
        """Detect AI-generated text using multiple providers"""
        if providers is None:
            providers = list(self.configs.keys())
        
        tasks = []
        for provider in providers:
            if provider in self.configs:
                tasks.append(self._detect_text_single(text, provider))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, DetectionResult):
                valid_results.append(result)
            else:
                logger.error(f"Detection failed: {result}")
        
        return valid_results
    
    async def _detect_text_single(
        self, 
        text: str, 
        provider: Provider
    ) -> DetectionResult:
        """Detect text with single provider"""
        cache_key = self._get_cache_key(text, provider, "text")
        
        # Check cache
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        # Make API request
        payload = {"text": text}
        
        try:
            response = await self._make_request(provider, "text", payload)
            
            # Parse provider-specific response
            result = self._parse_response(provider, response, "text")
            
            # Cache result
            self._save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting with {provider}: {e}")
            raise
    
    def _parse_response(
        self, 
        provider: Provider, 
        response: Dict, 
        content_type: str
    ) -> DetectionResult:
        """Parse provider-specific response format"""
        if provider == Provider.HIVE:
            ai_info = response.get("ai_generated", {})
            return DetectionResult(
                detected=ai_info.get("detected", False),
                confidence=ai_info.get("confidence", 0.0),
                provider=provider.value,
                details=response,
                timestamp=time.time()
            )
        elif provider == Provider.AZURE:
            # Azure returns harm categories
            harm_detected = any(
                cat.get("severity", 0) > 2 
                for cat in response.get("categoriesAnalysis", [])
            )
            return DetectionResult(
                detected=harm_detected,
                confidence=max(
                    cat.get("severity", 0) / 6 
                    for cat in response.get("categoriesAnalysis", [])
                ),
                provider=provider.value,
                details=response,
                timestamp=time.time()
            )
        # Add more provider-specific parsing
        
    async def detect_image(
        self, 
        image_url: str, 
        providers: Optional[List[Provider]] = None
    ) -> List[DetectionResult]:
        """Detect AI-generated images"""
        if providers is None:
            providers = list(self.configs.keys())
        
        tasks = []
        for provider in providers:
            if provider in self.configs and "image" in self.PROVIDER_ENDPOINTS[provider]:
                tasks.append(self._detect_image_single(image_url, provider))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for result in results:
            if isinstance(result, DetectionResult):
                valid_results.append(result)
        
        return valid_results
    
    async def _detect_image_single(
        self, 
        image_url: str, 
        provider: Provider
    ) -> DetectionResult:
        """Detect image with single provider"""
        cache_key = self._get_cache_key(image_url, provider, "image")
        
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        payload = {"url": image_url}
        
        try:
            response = await self._make_request(provider, "image", payload)
            result = self._parse_response(provider, response, "image")
            self._save_to_cache(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Error detecting image with {provider}: {e}")
            raise
    
    def get_consensus(self, results: List[DetectionResult]) -> Dict:
        """Calculate consensus from multiple detection results"""
        if not results:
            return {"consensus": False, "confidence": 0.0, "providers": 0}
        
        detected_count = sum(1 for r in results if r.detected)
        avg_confidence = sum(r.confidence for r in results) / len(results)
        
        # Weighted consensus based on confidence
        weighted_sum = sum(
            r.confidence if r.detected else (1 - r.confidence) 
            for r in results
        )
        weighted_avg = weighted_sum / len(results)
        
        return {
            "consensus": detected_count > len(results) / 2,
            "confidence": weighted_avg,
            "providers": len(results),
            "detected_count": detected_count,
            "details": [
                {
                    "provider": r.provider,
                    "detected": r.detected,
                    "confidence": r.confidence
                }
                for r in results
            ]
        }

# Usage example
async def main():
    # Configure multiple providers
    configs = [
        DetectionConfig(
            api_key="hive-api-key",
            provider=Provider.HIVE,
            cache_ttl=1800
        ),
        DetectionConfig(
            api_key="azure-api-key",
            provider=Provider.AZURE,
            timeout=45
        )
    ]
    
    service = AIDetectionService(configs)
    
    try:
        # Detect with all configured providers
        results = await service.detect_text(
            "This is a sample text to check for AI generation",
            providers=[Provider.HIVE, Provider.AZURE]
        )
        
        # Get consensus
        consensus = service.get_consensus(results)
        print(f"Consensus: {consensus}")
        
        # Detect image
        image_results = await service.detect_image(
            "https://example.com/image.jpg"
        )
        
        for result in image_results:
            print(f"{result.provider}: {result.detected} ({result.confidence:.2%})")
            
    finally:
        await service.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Node.js - Enterprise Client with TypeScript

```typescript
// install: npm install axios retry-axios lru-cache circuit-breaker-js winston

import axios, { AxiosInstance, AxiosError } from 'axios';
import axiosRetry from 'axios-retry';
import LRU from 'lru-cache';
import CircuitBreaker from 'circuit-breaker-js';
import crypto from 'crypto';
import { Logger } from 'winston';

// Types
export enum Provider {
    HIVE = 'hive',
    AZURE = 'azure',
    AWS = 'aws',
    GOOGLE = 'google',
    REALITY_DEFENDER = 'reality_defender'
}

export interface DetectionConfig {
    apiKey: string;
    provider: Provider;
    timeout?: number;
    maxRetries?: number;
    cacheTTL?: number;
}

export interface DetectionResult {
    detected: boolean;
    confidence: number;
    provider: string;
    details: any;
    timestamp: number;
    cached?: boolean;
}

export interface ConsensusResult {
    consensus: boolean;
    confidence: number;
    providers: number;
    detectedCount: number;
    details: Array<{
        provider: string;
        detected: boolean;
        confidence: number;
    }>;
}

// Main service class
export class AIDetectionService {
    private clients: Map<Provider, AxiosInstance> = new Map();
    private configs: Map<Provider, DetectionConfig> = new Map();
    private cache: LRU<string, DetectionResult>;
    private circuitBreakers: Map<Provider, any> = new Map();
    private logger: Logger;

    private static readonly ENDPOINTS = {
        [Provider.HIVE]: {
            base: 'https://api.thehive.ai/api/v2',
            text: '/ai-generated-content/text',
            image: '/ai-generated-content/image',
            video: '/deepfake/video'
        },
        [Provider.AZURE]: {
            base: 'https://{resource}.cognitiveservices.azure.com',
            text: '/contentsafety/text:analyze',
            image: '/contentsafety/image:analyze'
        },
        [Provider.AWS]: {
            base: 'https://rekognition.{region}.amazonaws.com',
            image: '/detect-moderation-labels'
        }
    };

    constructor(configs: DetectionConfig[], logger: Logger) {
        this.logger = logger;
        this.cache = new LRU<string, DetectionResult>({
            max: 1000,
            ttl: 1000 * 60 * 60 // 1 hour default
        });

        // Initialize providers
        configs.forEach(config => {
            this.initializeProvider(config);
        });
    }

    private initializeProvider(config: DetectionConfig): void {
        const client = axios.create({
            timeout: config.timeout || 30000,
            headers: this.getHeaders(config)
        });

        // Add retry logic
        axiosRetry(client, {
            retries: config.maxRetries || 3,
            retryDelay: axiosRetry.exponentialDelay,
            retryCondition: (error) => {
                return axiosRetry.isNetworkOrIdempotentRequestError(error) ||
                    (error.response?.status ?? 0) >= 500;
            }
        });

        // Add circuit breaker
        const breaker = new CircuitBreaker({
            windowDuration: 60000, // 1 minute
            numBuckets: 60,
            timeoutDuration: 30000,
            errorThreshold: 50,
            volumeThreshold: 10
        });

        this.clients.set(config.provider, client);
        this.configs.set(config.provider, config);
        this.circuitBreakers.set(config.provider, breaker);
    }

    private getHeaders(config: DetectionConfig): Record<string, string> {
        switch (config.provider) {
            case Provider.HIVE:
                return { 'Authorization': `Bearer ${config.apiKey}` };
            case Provider.AZURE:
                return { 'Ocp-Apim-Subscription-Key': config.apiKey };
            case Provider.AWS:
                // Simplified - actual implementation needs AWS signature
                return { 'Authorization': `AWS4-HMAC-SHA256 ${config.apiKey}` };
            default:
                return {};
        }
    }

    private getCacheKey(content: string, provider: Provider, type: string): string {
        const hash = crypto.createHash('sha256').update(content).digest('hex');
        return `${provider}:${type}:${hash}`;
    }

    private buildUrl(provider: Provider, endpoint: string): string {
        const endpoints = AIDetectionService.ENDPOINTS[provider];
        if (!endpoints) {
            throw new Error(`No endpoints configured for provider: ${provider}`);
        }

        let baseUrl = endpoints.base;
        
        // Replace placeholders
        if (provider === Provider.AZURE) {
            baseUrl = baseUrl.replace('{resource}', 'your-resource');
        } else if (provider === Provider.AWS) {
            baseUrl = baseUrl.replace('{region}', 'us-east-1');
        }

        return baseUrl + endpoints[endpoint];
    }

    async detectText(
        text: string,
        providers?: Provider[]
    ): Promise<DetectionResult[]> {
        const targetProviders = providers || Array.from(this.configs.keys());
        
        const promises = targetProviders.map(provider => 
            this.detectTextSingle(text, provider).catch(error => {
                this.logger.error(`Detection failed for ${provider}:`, error);
                return null;
            })
        );

        const results = await Promise.all(promises);
        return results.filter((r): r is DetectionResult => r !== null);
    }

    private async detectTextSingle(
        text: string,
        provider: Provider
    ): Promise<DetectionResult> {
        const cacheKey = this.getCacheKey(text, provider, 'text');
        
        // Check cache
        const cached = this.cache.get(cacheKey);
        if (cached) {
            return { ...cached, cached: true };
        }

        const client = this.clients.get(provider);
        const breaker = this.circuitBreakers.get(provider);
        
        if (!client || !breaker) {
            throw new Error(`Provider ${provider} not initialized`);
        }

        // Use circuit breaker
        return new Promise((resolve, reject) => {
            breaker.run(
                async (success: Function, failure: Function) => {
                    try {
                        const url = this.buildUrl(provider, 'text');
                        const response = await client.post(url, { text });
                        
                        const result = this.parseResponse(
                            provider,
                            response.data,
                            'text'
                        );
                        
                        // Cache result
                        this.cache.set(cacheKey, result);
                        
                        success();
                        resolve(result);
                    } catch (error) {
                        failure();
                        reject(error);
                    }
                },
                () => {
                    reject(new Error(`Circuit breaker open for ${provider}`));
                }
            );
        });
    }

    async detectImage(
        imageUrl: string,
        providers?: Provider[]
    ): Promise<DetectionResult[]> {
        const targetProviders = providers || Array.from(this.configs.keys());
        
        const promises = targetProviders.map(provider =>
            this.detectImageSingle(imageUrl, provider).catch(error => {
                this.logger.error(`Image detection failed for ${provider}:`, error);
                return null;
            })
        );

        const results = await Promise.all(promises);
        return results.filter((r): r is DetectionResult => r !== null);
    }

    private async detectImageSingle(
        imageUrl: string,
        provider: Provider
    ): Promise<DetectionResult> {
        const cacheKey = this.getCacheKey(imageUrl, provider, 'image');
        
        const cached = this.cache.get(cacheKey);
        if (cached) {
            return { ...cached, cached: true };
        }

        const client = this.clients.get(provider);
        const breaker = this.circuitBreakers.get(provider);
        
        if (!client || !breaker) {
            throw new Error(`Provider ${provider} not initialized`);
        }

        return new Promise((resolve, reject) => {
            breaker.run(
                async (success: Function, failure: Function) => {
                    try {
                        const url = this.buildUrl(provider, 'image');
                        const response = await client.post(url, { url: imageUrl });
                        
                        const result = this.parseResponse(
                            provider,
                            response.data,
                            'image'
                        );
                        
                        this.cache.set(cacheKey, result);
                        
                        success();
                        resolve(result);
                    } catch (error) {
                        failure();
                        reject(error);
                    }
                },
                () => {
                    reject(new Error(`Circuit breaker open for ${provider}`));
                }
            );
        });
    }

    private parseResponse(
        provider: Provider,
        response: any,
        type: string
    ): DetectionResult {
        switch (provider) {
            case Provider.HIVE:
                const aiInfo = response.ai_generated || {};
                return {
                    detected: aiInfo.detected || false,
                    confidence: aiInfo.confidence || 0,
                    provider: provider,
                    details: response,
                    timestamp: Date.now()
                };
            
            case Provider.AZURE:
                const categories = response.categoriesAnalysis || [];
                const maxSeverity = Math.max(
                    ...categories.map((c: any) => c.severity || 0)
                );
                return {
                    detected: maxSeverity > 2,
                    confidence: maxSeverity / 6,
                    provider: provider,
                    details: response,
                    timestamp: Date.now()
                };
            
            default:
                return {
                    detected: false,
                    confidence: 0,
                    provider: provider,
                    details: response,
                    timestamp: Date.now()
                };
        }
    }

    getConsensus(results: DetectionResult[]): ConsensusResult {
        if (results.length === 0) {
            return {
                consensus: false,
                confidence: 0,
                providers: 0,
                detectedCount: 0,
                details: []
            };
        }

        const detectedCount = results.filter(r => r.detected).length;
        const avgConfidence = results.reduce((sum, r) => sum + r.confidence, 0) / results.length;
        
        const weightedSum = results.reduce((sum, r) => {
            return sum + (r.detected ? r.confidence : 1 - r.confidence);
        }, 0);
        const weightedAvg = weightedSum / results.length;

        return {
            consensus: detectedCount > results.length / 2,
            confidence: weightedAvg,
            providers: results.length,
            detectedCount: detectedCount,
            details: results.map(r => ({
                provider: r.provider,
                detected: r.detected,
                confidence: r.confidence
            }))
        };
    }

    // Stream processing for large batches
    async *detectStream<T extends { id: string; content: string; type: 'text' | 'image' }>(
        items: T[],
        batchSize: number = 10
    ): AsyncGenerator<{ item: T; results: DetectionResult[] }> {
        for (let i = 0; i < items.length; i += batchSize) {
            const batch = items.slice(i, i + batchSize);
            
            const batchResults = await Promise.all(
                batch.map(async (item) => {
                    const results = item.type === 'text'
                        ? await this.detectText(item.content)
                        : await this.detectImage(item.content);
                    
                    return { item, results };
                })
            );

            for (const result of batchResults) {
                yield result;
            }
        }
    }

    // Health check
    async healthCheck(): Promise<Record<Provider, boolean>> {
        const health: Record<Provider, boolean> = {} as any;
        
        for (const provider of this.configs.keys()) {
            try {
                // Simple test with minimal content
                await this.detectTextSingle('test', provider);
                health[provider] = true;
            } catch (error) {
                health[provider] = false;
            }
        }
        
        return health;
    }
}

// Usage example
import winston from 'winston';

const logger = winston.createLogger({
    level: 'info',
    format: winston.format.json(),
    transports: [
        new winston.transports.Console()
    ]
});

async function main() {
    const configs: DetectionConfig[] = [
        {
            apiKey: process.env.HIVE_API_KEY!,
            provider: Provider.HIVE,
            cacheTTL: 1800000 // 30 minutes
        },
        {
            apiKey: process.env.AZURE_API_KEY!,
            provider: Provider.AZURE,
            timeout: 45000
        }
    ];

    const service = new AIDetectionService(configs, logger);

    // Single detection
    const results = await service.detectText(
        'This is a sample text to check'
    );

    const consensus = service.getConsensus(results);
    console.log('Consensus:', consensus);

    // Batch processing with stream
    const items = [
        { id: '1', content: 'Text 1', type: 'text' as const },
        { id: '2', content: 'Text 2', type: 'text' as const },
        { id: '3', content: 'https://example.com/image.jpg', type: 'image' as const }
    ];

    for await (const result of service.detectStream(items, 2)) {
        console.log(`Item ${result.item.id}:`, result.results);
    }

    // Health check
    const health = await service.healthCheck();
    console.log('Provider health:', health);
}

main().catch(console.error);
```

## Framework-Specific Integrations

### Django Integration

```python
# detection/services.py
from django.conf import settings
from django.core.cache import cache
from django.db import models
import asyncio
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class AIDetectionResult(models.Model):
    """Model to store detection results"""
    content_hash = models.CharField(max_length=64, db_index=True)
    provider = models.CharField(max_length=50)
    detected = models.BooleanField()
    confidence = models.FloatField()
    details = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['content_hash', 'provider']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['detected', 'confidence'])
        ]

class DjangoAIDetectionService:
    """Django-specific AI detection service with DB caching"""
    
    def __init__(self):
        self.detector = AIDetectionService(
            configs=self._get_configs_from_settings()
        )
    
    def _get_configs_from_settings(self):
        """Load configurations from Django settings"""
        configs = []
        for provider_config in settings.AI_DETECTION_PROVIDERS:
            configs.append(DetectionConfig(**provider_config))
        return configs
    
    def detect_and_store(self, content: str, content_type: str = 'text'):
        """Detect and store results in database"""
        # Check cache first
        cache_key = f"ai_detection:{hashlib.sha256(content.encode()).hexdigest()}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Run detection
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            if content_type == 'text':
                results = loop.run_until_complete(
                    self.detector.detect_text(content)
                )
            else:
                results = loop.run_until_complete(
                    self.detector.detect_image(content)
                )
            
            # Store in database
            for result in results:
                AIDetectionResult.objects.update_or_create(
                    content_hash=hashlib.sha256(content.encode()).hexdigest(),
                    provider=result.provider,
                    defaults={
                        'detected': result.detected,
                        'confidence': result.confidence,
                        'details': result.details
                    }
                )
            
            # Cache results
            consensus = self.detector.get_consensus(results)
            cache.set(cache_key, consensus, timeout=3600)
            
            return consensus
            
        finally:
            loop.close()

# detection/views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
import json

class AIDetectionView(View):
    """API endpoint for AI detection"""
    
    def __init__(self):
        super().__init__()
        self.service = DjangoAIDetectionService()
    
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            content = data.get('content')
            content_type = data.get('type', 'text')
            
            if not content:
                return JsonResponse(
                    {'error': 'Content is required'}, 
                    status=400
                )
            
            result = self.service.detect_and_store(content, content_type)
            
            return JsonResponse({
                'success': True,
                'result': result
            })
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return JsonResponse(
                {'error': 'Detection failed'}, 
                status=500
            )

# detection/middleware.py
class AIContentModerationMiddleware:
    """Middleware to automatically moderate user-generated content"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.service = DjangoAIDetectionService()
    
    def __call__(self, request):
        # Check if request contains user content
        if request.method == 'POST' and request.path.startswith('/api/posts/'):
            try:
                data = json.loads(request.body)
                if 'content' in data:
                    result = self.service.detect_and_store(
                        data['content'], 
                        'text'
                    )
                    
                    if result['consensus'] and result['confidence'] > 0.8:
                        return JsonResponse(
                            {'error': 'AI-generated content detected'}, 
                            status=400
                        )
            except:
                pass
        
        response = self.get_response(request)
        return response

# settings.py
AI_DETECTION_PROVIDERS = [
    {
        'api_key': os.environ.get('HIVE_API_KEY'),
        'provider': 'hive',
        'cache_ttl': 1800
    },
    {
        'api_key': os.environ.get('AZURE_API_KEY'),
        'provider': 'azure',
        'timeout': 30
    }
]

MIDDLEWARE = [
    # ... other middleware
    'detection.middleware.AIContentModerationMiddleware',
]
```

### Express.js Integration

```javascript
// aiDetection.middleware.js
const { AIDetectionService, Provider } = require('./aiDetectionService');
const redis = require('redis');
const { promisify } = require('util');

class AIDetectionMiddleware {
    constructor(configs) {
        this.service = new AIDetectionService(configs);
        this.redisClient = redis.createClient({
            host: process.env.REDIS_HOST || 'localhost',
            port: process.env.REDIS_PORT || 6379
        });
        
        this.getAsync = promisify(this.redisClient.get).bind(this.redisClient);
        this.setAsync = promisify(this.redisClient.setex).bind(this.redisClient);
    }

    // Middleware for automatic content moderation
    moderateContent(options = {}) {
        const {
            threshold = 0.8,
            blockOnDetection = true,
            contentFields = ['content', 'text', 'message']
        } = options;

        return async (req, res, next) => {
            try {
                // Extract content from request
                let content = null;
                for (const field of contentFields) {
                    if (req.body && req.body[field]) {
                        content = req.body[field];
                        break;
                    }
                }

                if (!content) {
                    return next();
                }

                // Check cache
                const cacheKey = `ai_detection:${this.hashContent(content)}`;
                const cached = await this.getAsync(cacheKey);
                
                if (cached) {
                    const result = JSON.parse(cached);
                    req.aiDetection = result;
                    
                    if (blockOnDetection && result.consensus && result.confidence > threshold) {
                        return res.status(400).json({
                            error: 'AI-generated content detected',
                            detection: result
                        });
                    }
                    
                    return next();
                }

                // Perform detection
                const results = await this.service.detectText(content);
                const consensus = this.service.getConsensus(results);
                
                // Cache result
                await this.setAsync(cacheKey, 3600, JSON.stringify(consensus));
                
                // Attach to request
                req.aiDetection = consensus;
                
                // Block if needed
                if (blockOnDetection && consensus.consensus && consensus.confidence > threshold) {
                    return res.status(400).json({
                        error: 'AI-generated content detected',
                        detection: consensus
                    });
                }
                
                next();
            } catch (error) {
                console.error('AI detection error:', error);
                // Don't block on error
                next();
            }
        };
    }

    // Middleware for adding detection headers
    addDetectionHeaders() {
        return async (req, res, next) => {
            if (req.aiDetection) {
                res.setHeader('X-AI-Detected', req.aiDetection.consensus);
                res.setHeader('X-AI-Confidence', req.aiDetection.confidence.toFixed(2));
                res.setHeader('X-AI-Providers', req.aiDetection.providers);
            }
            next();
        };
    }

    // Rate limiting based on AI detection
    aiBasedRateLimit(options = {}) {
        const {
            windowMs = 60000,
            maxRequests = 100,
            aiMultiplier = 0.5 // AI content gets half the rate limit
        } = options;

        const requests = new Map();

        return async (req, res, next) => {
            const key = req.ip;
            const now = Date.now();
            
            // Clean old entries
            for (const [k, v] of requests.entries()) {
                if (now - v.timestamp > windowMs) {
                    requests.delete(k);
                }
            }

            // Get current count
            const current = requests.get(key) || { count: 0, timestamp: now };
            
            // Apply multiplier if AI detected
            const increment = req.aiDetection?.consensus ? 1 / aiMultiplier : 1;
            current.count += increment;
            
            requests.set(key, current);
            
            // Check limit
            if (current.count > maxRequests) {
                return res.status(429).json({
                    error: 'Rate limit exceeded',
                    retryAfter: Math.ceil(windowMs / 1000)
                });
            }
            
            next();
        };
    }

    hashContent(content) {
        return require('crypto')
            .createHash('sha256')
            .update(content)
            .digest('hex');
    }
}

// Express app setup
const express = require('express');
const winston = require('winston');

const app = express();
app.use(express.json());

// Logger setup
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.json(),
    transports: [
        new winston.transports.File({ filename: 'ai-detection.log' }),
        new winston.transports.Console()
    ]
});

// Initialize AI detection
const aiDetection = new AIDetectionMiddleware([
    {
        apiKey: process.env.HIVE_API_KEY,
        provider: Provider.HIVE
    },
    {
        apiKey: process.env.AZURE_API_KEY,
        provider: Provider.AZURE
    }
], logger);

// Apply middleware
app.use(aiDetection.moderateContent({
    threshold: 0.7,
    blockOnDetection: false // Just flag, don't block
}));

app.use(aiDetection.addDetectionHeaders());
app.use(aiDetection.aiBasedRateLimit());

// API endpoint
app.post('/api/detect', async (req, res) => {
    try {
        const { content, type = 'text' } = req.body;
        
        if (!content) {
            return res.status(400).json({ error: 'Content required' });
        }
        
        const results = type === 'text'
            ? await aiDetection.service.detectText(content)
            : await aiDetection.service.detectImage(content);
        
        const consensus = aiDetection.service.getConsensus(results);
        
        res.json({
            success: true,
            results: consensus,
            providers: results.map(r => ({
                provider: r.provider,
                detected: r.detected,
                confidence: r.confidence
            }))
        });
    } catch (error) {
        logger.error('Detection error:', error);
        res.status(500).json({ error: 'Detection failed' });
    }
});

// Protected route example
app.post('/api/posts', async (req, res) => {
    // AI detection already performed by middleware
    if (req.aiDetection) {
        logger.info('Content AI detection:', req.aiDetection);
    }
    
    // Your post creation logic here
    res.json({
        success: true,
        message: 'Post created',
        aiDetection: req.aiDetection
    });
});

// WebSocket support for real-time detection
const WebSocket = require('ws');
const server = require('http').createServer(app);
const wss = new WebSocket.Server({ server });

wss.on('connection', (ws) => {
    ws.on('message', async (message) => {
        try {
            const data = JSON.parse(message);
            
            if (data.type === 'detect') {
                const results = await aiDetection.service.detectText(data.content);
                const consensus = aiDetection.service.getConsensus(results);
                
                ws.send(JSON.stringify({
                    type: 'detection_result',
                    result: consensus
                }));
            }
        } catch (error) {
            ws.send(JSON.stringify({
                type: 'error',
                message: 'Detection failed'
            }));
        }
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
```

## Error Handling and Resilience

### Comprehensive Error Handling Pattern

```python
from enum import Enum
from typing import Optional, Dict, List, Union
import traceback
from dataclasses import dataclass
import asyncio
from datetime import datetime, timedelta

class ErrorType(Enum):
    NETWORK = "network"
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    INVALID_CONTENT = "invalid_content"
    PROVIDER_ERROR = "provider_error"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"

@dataclass
class DetectionError:
    error_type: ErrorType
    message: str
    provider: Optional[str] = None
    retry_after: Optional[int] = None
    details: Optional[Dict] = None

class ErrorHandler:
    """Centralized error handling for AI detection"""
    
    def __init__(self, logger):
        self.logger = logger
        self.error_counts = {}
        self.last_errors = {}
    
    def handle_error(self, error: Exception, provider: str) -> DetectionError:
        """Categorize and handle different error types"""
        
        # Track error frequency
        self._track_error(provider, error)
        
        # Categorize error
        if isinstance(error, asyncio.TimeoutError):
            return DetectionError(
                error_type=ErrorType.TIMEOUT,
                message="Request timed out",
                provider=provider
            )
        
        elif isinstance(error, aiohttp.ClientError):
            return self._handle_client_error(error, provider)
        
        elif hasattr(error, 'response'):
            return self._handle_response_error(error, provider)
        
        else:
            return DetectionError(
                error_type=ErrorType.UNKNOWN,
                message=str(error),
                provider=provider,
                details={'traceback': traceback.format_exc()}
            )
    
    def _handle_client_error(self, error: aiohttp.ClientError, provider: str) -> DetectionError:
        """Handle aiohttp client errors"""
        if isinstance(error, aiohttp.ClientConnectorError):
            return DetectionError(
                error_type=ErrorType.NETWORK,
                message="Network connection failed",
                provider=provider
            )
        
        elif isinstance(error, aiohttp.ClientResponseError):
            if error.status == 429:
                retry_after = error.headers.get('Retry-After', 60)
                return DetectionError(
                    error_type=ErrorType.RATE_LIMIT,
                    message="Rate limit exceeded",
                    provider=provider,
                    retry_after=int(retry_after)
                )
            elif error.status in [401, 403]:
                return DetectionError(
                    error_type=ErrorType.AUTHENTICATION,
                    message="Authentication failed",
                    provider=provider
                )
            elif error.status >= 500:
                return DetectionError(
                    error_type=ErrorType.PROVIDER_ERROR,
                    message=f"Provider error: {error.status}",
                    provider=provider
                )
        
        return DetectionError(
            error_type=ErrorType.UNKNOWN,
            message=str(error),
            provider=provider
        )
    
    def _handle_response_error(self, error: Exception, provider: str) -> DetectionError:
        """Handle errors with response attribute"""
        response = getattr(error, 'response', None)
        if not response:
            return DetectionError(
                error_type=ErrorType.UNKNOWN,
                message=str(error),
                provider=provider
            )
        
        status_code = getattr(response, 'status_code', 0)
        
        if status_code == 429:
            retry_after = response.headers.get('Retry-After', 60)
            return DetectionError(
                error_type=ErrorType.RATE_LIMIT,
                message="Rate limit exceeded",
                provider=provider,
                retry_after=int(retry_after)
            )
        
        # Add more status code handling as needed
        
        return DetectionError(
            error_type=ErrorType.PROVIDER_ERROR,
            message=f"HTTP {status_code}: {getattr(response, 'text', '')}",
            provider=provider
        )
    
    def _track_error(self, provider: str, error: Exception):
        """Track error frequency for monitoring"""
        key = f"{provider}:{type(error).__name__}"
        
        if key not in self.error_counts:
            self.error_counts[key] = []
        
        self.error_counts[key].append(datetime.utcnow())
        self.last_errors[key] = str(error)
        
        # Clean old errors
        cutoff = datetime.utcnow() - timedelta(hours=1)
        self.error_counts[key] = [
            ts for ts in self.error_counts[key] if ts > cutoff
        ]
    
    def get_error_stats(self) -> Dict:
        """Get error statistics for monitoring"""
        stats = {}
        for key, timestamps in self.error_counts.items():
            provider, error_type = key.split(':', 1)
            
            if provider not in stats:
                stats[provider] = {}
            
            stats[provider][error_type] = {
                'count': len(timestamps),
                'last_error': self.last_errors.get(key, ''),
                'last_occurrence': max(timestamps).isoformat() if timestamps else None
            }
        
        return stats

class ResilientAIDetectionService(AIDetectionService):
    """Enhanced service with comprehensive error handling"""
    
    def __init__(self, configs: List[DetectionConfig], logger):
        super().__init__(configs)
        self.error_handler = ErrorHandler(logger)
        self.logger = logger
        self.retry_delays = {}  # Track retry delays per provider
    
    async def detect_with_fallback(
        self, 
        content: str,
        content_type: str = 'text',
        providers: Optional[List[Provider]] = None
    ) -> Union[List[DetectionResult], List[DetectionError]]:
        """Detect with automatic fallback and error handling"""
        
        if providers is None:
            providers = list(self.configs.keys())
        
        results = []
        errors = []
        
        for provider in providers:
            # Check if provider is in retry delay
            if self._is_in_retry_delay(provider):
                self.logger.info(f"Skipping {provider} due to retry delay")
                continue
            
            try:
                if content_type == 'text':
                    result = await self._detect_text_single(content, provider)
                else:
                    result = await self._detect_image_single(content, provider)
                
                results.append(result)
                
                # Clear any retry delay on success
                self._clear_retry_delay(provider)
                
            except Exception as e:
                error = self.error_handler.handle_error(e, provider.value)
                errors.append(error)
                
                # Set retry delay if needed
                if error.retry_after:
                    self._set_retry_delay(provider, error.retry_after)
                
                self.logger.error(
                    f"Detection failed for {provider}: {error.message}",
                    extra={
                        'provider': provider.value,
                        'error_type': error.error_type.value,
                        'details': error.details
                    }
                )
                
                # Continue to next provider
                continue
        
        # If all providers failed, raise the last error
        if not results and errors:
            raise Exception(f"All providers failed. Errors: {errors}")
        
        return results
    
    def _is_in_retry_delay(self, provider: Provider) -> bool:
        """Check if provider is still in retry delay period"""
        if provider not in self.retry_delays:
            return False
        
        return datetime.utcnow() < self.retry_delays[provider]
    
    def _set_retry_delay(self, provider: Provider, seconds: int):
        """Set retry delay for a provider"""
        self.retry_delays[provider] = datetime.utcnow() + timedelta(seconds=seconds)
        self.logger.info(f"Set retry delay for {provider}: {seconds}s")
    
    def _clear_retry_delay(self, provider: Provider):
        """Clear retry delay for a provider"""
        if provider in self.retry_delays:
            del self.retry_delays[provider]
    
    async def detect_with_retry_strategy(
        self,
        content: str,
        content_type: str = 'text',
        max_attempts: int = 3
    ) -> Dict:
        """Advanced retry strategy with exponential backoff"""
        
        for attempt in range(max_attempts):
            try:
                # Try detection
                results = await self.detect_with_fallback(
                    content, 
                    content_type
                )
                
                if results:
                    return {
                        'success': True,
                        'results': results,
                        'consensus': self.get_consensus(results),
                        'attempts': attempt + 1
                    }
                
            except Exception as e:
                if attempt == max_attempts - 1:
                    # Last attempt failed
                    return {
                        'success': False,
                        'error': str(e),
                        'attempts': attempt + 1,
                        'error_stats': self.error_handler.get_error_stats()
                    }
                
                # Exponential backoff
                delay = (2 ** attempt) + random.uniform(0, 1)
                self.logger.info(f"Retrying after {delay:.2f}s (attempt {attempt + 1})")
                await asyncio.sleep(delay)
        
        return {
            'success': False,
            'error': 'Max attempts reached',
            'attempts': max_attempts
        }

# Usage with error handling
async def robust_detection_example():
    logger = logging.getLogger(__name__)
    
    configs = [
        DetectionConfig(
            api_key="key1",
            provider=Provider.HIVE
        ),
        DetectionConfig(
            api_key="key2",
            provider=Provider.AZURE
        )
    ]
    
    service = ResilientAIDetectionService(configs, logger)
    
    # Detection with automatic retry and fallback
    result = await service.detect_with_retry_strategy(
        "Content to check",
        max_attempts=3
    )
    
    if result['success']:
        print(f"Detection successful: {result['consensus']}")
    else:
        print(f"Detection failed: {result['error']}")
        print(f"Error statistics: {result['error_stats']}")
```

## Testing and Validation

### Comprehensive Test Suite

```python
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import aiohttp
from typing import Dict, List

class TestAIDetectionService:
    """Comprehensive test suite for AI detection service"""
    
    @pytest.fixture
    def mock_configs(self):
        return [
            DetectionConfig(
                api_key="test-key-1",
                provider=Provider.HIVE,
                cache_ttl=60
            ),
            DetectionConfig(
                api_key="test-key-2",
                provider=Provider.AZURE,
                timeout=10
            )
        ]
    
    @pytest.fixture
    async def service(self, mock_configs):
        service = AIDetectionService(mock_configs)
        yield service
        await service.close()
    
    @pytest.mark.asyncio
    async def test_text_detection_success(self, service):
        """Test successful text detection"""
        mock_response = {
            "ai_generated": {
                "detected": True,
                "confidence": 0.95
            }
        }
        
        with patch.object(
            service, 
            '_make_request',
            return_value=mock_response
        ) as mock_request:
            results = await service.detect_text(
                "Test text",
                providers=[Provider.HIVE]
            )
            
            assert len(results) == 1
            assert results[0].detected is True
            assert results[0].confidence == 0.95
            assert results[0].provider == Provider.HIVE.value
            
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_caching(self, service):
        """Test that caching works correctly"""
        mock_response = {
            "ai_generated": {
                "detected": False,
                "confidence": 0.1
            }
        }
        
        with patch.object(
            service,
            '_make_request',
            return_value=mock_response
        ) as mock_request:
            # First call
            result1 = await service.detect_text(
                "Cached text",
                providers=[Provider.HIVE]
            )
            
            # Second call (should use cache)
            result2 = await service.detect_text(
                "Cached text",
                providers=[Provider.HIVE]
            )
            
            # Request should only be made once
            assert mock_request.call_count == 1
            
            # Results should be the same
            assert result1[0].detected == result2[0].detected
            assert result2[0].cached is True
    
    @pytest.mark.asyncio
    async def test_circuit_breaker(self, service):
        """Test circuit breaker functionality"""
        # Simulate multiple failures
        with patch.object(
            service,
            '_make_request',
            side_effect=aiohttp.ClientError("Connection failed")
        ):
            # Make requests until circuit breaker opens
            for i in range(6):
                try:
                    await service.detect_text(
                        f"Text {i}",
                        providers=[Provider.HIVE]
                    )
                except:
                    pass
            
            # Circuit should be open now
            with pytest.raises(Exception) as exc_info:
                await service.detect_text(
                    "Should fail",
                    providers=[Provider.HIVE]
                )
            
            assert "Circuit breaker" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_consensus_calculation(self, service):
        """Test consensus calculation"""
        results = [
            DetectionResult(
                detected=True,
                confidence=0.9,
                provider="hive",
                details={},
                timestamp=time.time()
            ),
            DetectionResult(
                detected=True,
                confidence=0.8,
                provider="azure",
                details={},
                timestamp=time.time()
            ),
            DetectionResult(
                detected=False,
                confidence=0.3,
                provider="aws",
                details={},
                timestamp=time.time()
            )
        ]
        
        consensus = service.get_consensus(results)
        
        assert consensus['consensus'] is True
        assert consensus['providers'] == 3
        assert consensus['detected_count'] == 2
        assert 0 < consensus['confidence'] < 1
    
    @pytest.mark.asyncio
    async def test_retry_logic(self, service):
        """Test retry logic with backoff"""
        call_count = 0
        
        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise aiohttp.ClientError("Temporary failure")
            return {"ai_generated": {"detected": True, "confidence": 0.9}}
        
        with patch.object(service, '_make_request', side_effect=mock_request):
            results = await service.detect_text(
                "Retry test",
                providers=[Provider.HIVE]
            )
            
            assert call_count == 3
            assert len(results) == 1
            assert results[0].detected is True

class TestErrorHandling:
    """Test error handling capabilities"""
    
    @pytest.fixture
    def error_handler(self):
        logger = Mock()
        return ErrorHandler(logger)
    
    def test_timeout_error_handling(self, error_handler):
        """Test timeout error categorization"""
        error = asyncio.TimeoutError()
        result = error_handler.handle_error(error, "test_provider")
        
        assert result.error_type == ErrorType.TIMEOUT
        assert result.provider == "test_provider"
    
    def test_rate_limit_error_handling(self, error_handler):
        """Test rate limit error handling"""
        response = Mock()
        response.status = 429
        response.headers = {'Retry-After': '120'}
        
        error = aiohttp.ClientResponseError(
            request_info=Mock(),
            history=(),
            status=429,
            headers=response.headers
        )
        
        result = error_handler.handle_error(error, "test_provider")
        
        assert result.error_type == ErrorType.RATE_LIMIT
        assert result.retry_after == 120
    
    def test_error_tracking(self, error_handler):
        """Test error frequency tracking"""
        # Generate multiple errors
        for i in range(5):
            error = ValueError(f"Test error {i}")
            error_handler.handle_error(error, "provider1")
        
        stats = error_handler.get_error_stats()
        
        assert "provider1" in stats
        assert "ValueError" in stats["provider1"]
        assert stats["provider1"]["ValueError"]["count"] == 5

# Integration tests
class TestIntegration:
    """Integration tests with real-like scenarios"""
    
    @pytest.mark.asyncio
    async def test_multi_provider_detection(self):
        """Test detection with multiple providers"""
        # Mock responses for different providers
        hive_response = {
            "ai_generated": {"detected": True, "confidence": 0.95}
        }
        azure_response = {
            "categoriesAnalysis": [
                {"category": "ai_generated", "severity": 5}
            ]
        }
        
        configs = [
            DetectionConfig(api_key="key1", provider=Provider.HIVE),
            DetectionConfig(api_key="key2", provider=Provider.AZURE)
        ]
        
        service = AIDetectionService(configs)
        
        with patch.object(service, '_make_request') as mock_request:
            mock_request.side_effect = [hive_response, azure_response]
            
            results = await service.detect_text("Test content")
            
            assert len(results) == 2
            assert any(r.provider == Provider.HIVE.value for r in results)
            assert any(r.provider == Provider.AZURE.value for r in results)
        
        await service.close()
    
    @pytest.mark.asyncio
    async def test_batch_processing(self):
        """Test batch processing capabilities"""
        configs = [DetectionConfig(api_key="key", provider=Provider.HIVE)]
        service = AIDetectionService(configs)
        
        items = [
            {"id": f"item_{i}", "content": f"Text {i}", "type": "text"}
            for i in range(10)
        ]
        
        with patch.object(
            service,
            '_make_request',
            return_value={"ai_generated": {"detected": False, "confidence": 0.1}}
        ):
            processed = 0
            async for result in service.detect_stream(items, batch_size=3):
                processed += 1
                assert 'item' in result
                assert 'results' in result
            
            assert processed == 10
        
        await service.close()

# Performance tests
class TestPerformance:
    """Performance and load tests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        configs = [DetectionConfig(api_key="key", provider=Provider.HIVE)]
        service = AIDetectionService(configs)
        
        with patch.object(
            service,
            '_make_request',
            return_value={"ai_generated": {"detected": True, "confidence": 0.9}}
        ):
            # Create 100 concurrent requests
            tasks = [
                service.detect_text(f"Text {i}", providers=[Provider.HIVE])
                for i in range(100)
            ]
            
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            assert len(results) == 100
            assert all(len(r) == 1 for r in results)
            
            # Should complete within reasonable time
            assert end_time - start_time < 5.0
        
        await service.close()
    
    @pytest.mark.asyncio
    async def test_memory_usage_with_cache(self):
        """Test memory usage doesn't grow unbounded with cache"""
        configs = [
            DetectionConfig(
                api_key="key",
                provider=Provider.HIVE,
                cache_ttl=1  # Very short TTL
            )
        ]
        service = AIDetectionService(configs)
        
        with patch.object(
            service,
            '_make_request',
            return_value={"ai_generated": {"detected": False, "confidence": 0.1}}
        ):
            # Generate many unique texts
            for i in range(1000):
                await service.detect_text(f"Unique text {i}")
            
            # Cache should not grow unbounded
            assert len(service.cache) < 1000
        
        await service.close()

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Load Testing Script

```python
import asyncio
import time
import statistics
from typing import List, Dict
import aiohttp
import json

class LoadTester:
    """Load testing for AI detection APIs"""
    
    def __init__(self, service: AIDetectionService):
        self.service = service
        self.results = []
    
    async def run_load_test(
        self,
        num_requests: int,
        concurrent_requests: int,
        content_generator=None
    ):
        """Run load test with specified parameters"""
        
        if content_generator is None:
            content_generator = lambda i: f"Test content {i}"
        
        print(f"Starting load test: {num_requests} requests, {concurrent_requests} concurrent")
        
        start_time = time.time()
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrent_requests)
        
        async def make_request(index):
            async with semaphore:
                request_start = time.time()
                
                try:
                    content = content_generator(index)
                    results = await self.service.detect_text(content)
                    
                    request_time = time.time() - request_start
                    
                    return {
                        'index': index,
                        'success': True,
                        'time': request_time,
                        'results': len(results),
                        'consensus': self.service.get_consensus(results)
                    }
                
                except Exception as e:
                    request_time = time.time() - request_start
                    
                    return {
                        'index': index,
                        'success': False,
                        'time': request_time,
                        'error': str(e)
                    }
        
        # Execute all requests
        tasks = [make_request(i) for i in range(num_requests)]
        self.results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]
        response_times = [r['time'] for r in successful]
        
        stats = {
            'total_requests': num_requests,
            'successful_requests': len(successful),
            'failed_requests': len(failed),
            'total_time': total_time,
            'requests_per_second': num_requests / total_time,
            'average_response_time': statistics.mean(response_times) if response_times else 0,
            'median_response_time': statistics.median(response_times) if response_times else 0,
            'p95_response_time': self._percentile(response_times, 95) if response_times else 0,
            'p99_response_time': self._percentile(response_times, 99) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0
        }
        
        return stats
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0
        
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def print_results(self, stats: Dict):
        """Print load test results"""
        print("\n" + "="*50)
        print("LOAD TEST RESULTS")
        print("="*50)
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Successful: {stats['successful_requests']}")
        print(f"Failed: {stats['failed_requests']}")
        print(f"Total Time: {stats['total_time']:.2f}s")
        print(f"Requests/Second: {stats['requests_per_second']:.2f}")
        print("\nResponse Times:")
        print(f"  Average: {stats['average_response_time']:.3f}s")
        print(f"  Median: {stats['median_response_time']:.3f}s")
        print(f"  95th Percentile: {stats['p95_response_time']:.3f}s")
        print(f"  99th Percentile: {stats['p99_response_time']:.3f}s")
        print(f"  Min: {stats['min_response_time']:.3f}s")
        print(f"  Max: {stats['max_response_time']:.3f}s")
        
        if stats['failed_requests'] > 0:
            print("\nError Summary:")
            errors = {}
            for r in self.results:
                if not r['success']:
                    error = r.get('error', 'Unknown')
                    errors[error] = errors.get(error, 0) + 1
            
            for error, count in errors.items():
                print(f"  {error}: {count}")

# Run load test
async def main():
    configs = [
        DetectionConfig(
            api_key="your-api-key",
            provider=Provider.HIVE
        )
    ]
    
    service = AIDetectionService(configs)
    tester = LoadTester(service)
    
    # Test with varying content
    def content_generator(index):
        templates = [
            "This is a test message number {}",
            "AI-generated content check for item {}",
            "Sample text for detection test {}"
        ]
        return templates[index % len(templates)].format(index)
    
    # Run different load scenarios
    scenarios = [
        (100, 10, "Light load"),
        (500, 50, "Medium load"),
        (1000, 100, "Heavy load")
    ]
    
    for num_requests, concurrent, name in scenarios:
        print(f"\n\nRunning {name} scenario...")
        stats = await tester.run_load_test(
            num_requests=num_requests,
            concurrent_requests=concurrent,
            content_generator=content_generator
        )
        tester.print_results(stats)
        
        # Save detailed results
        with open(f'load_test_{name.replace(" ", "_")}.json', 'w') as f:
            json.dump({
                'stats': stats,
                'results': tester.results[:100]  # First 100 for analysis
            }, f, indent=2)
    
    await service.close()

if __name__ == "__main__":
    asyncio.run(main())
```

This comprehensive guide provides production-ready code examples for integrating AI detection APIs across multiple languages and frameworks, with robust error handling, testing, and performance optimization strategies.