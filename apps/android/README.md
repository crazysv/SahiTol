# SahiTol Android Collector Application

Native Android application engineered for independent informal e-waste collectors in India. Built for offline resilience, high legibility, and low literacy using bilingual Hindi and Marathi layouts.

## Architecture
- **Language & UI**: Kotlin, Jetpack Compose, Material 3, Navigation Compose
- **Architecture Pattern**: MVVM with unidirectional data flow (Coroutines, StateFlow)
- **Local Persistence**: Room SQLite database with transactional outbox pattern
- **Offline Sync**: Android WorkManager with exponential backoff and stable idempotency keys
- **Hardware Integrations**: CameraX for photo evidence, Fused Location Provider
- **Edge AI**: LiteRT (`com.google.ai.edge.litert`) for on-device quantized model inference
- **Handover Verification**: ZXing QR decoding and SAHITOL-JCS-1 SHA-256 hash checking

## Pinned Toolchain
- **JDK**: OpenJDK 17 (Microsoft 17.0.20.1 LTS)
- **Android Gradle Plugin (AGP)**: 8.7.0
- **Gradle Wrapper**: 8.10.2
- **Kotlin**: 2.0.20 (Compose Compiler integrated)
- **Compile SDK**: 35 (Android 15)
- **Target SDK**: 35
- **Min SDK**: 26 (Android 8.0 Oreo)

## Local Development & Build

1. Ensure `local.properties` specifies your Android SDK directory:
   ```properties
   sdk.dir=C\:\\Users\\sarth\\AppData\\Local\\Android\\Sdk
   ```
2. Run unit test suite:
   ```bash
   ./gradlew test
   ```
3. Assemble debug APK:
   ```bash
   ./gradlew assembleDebug
   ```

## UI Gate Status
In compliance with `docs/05_DESIGN_STITCH.md`, the UI design is gated by the owner Stitch workflow. The initial diagnostic screen S00 is currently requested. The underlying Room persistence, outbox schema, domain pricing calculations, and permissions are fully implemented.
