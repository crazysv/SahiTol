# Proguard rules for SahiTol Android Collector app
-keepattributes *Annotation*
-keepclassmembers class * {
    @androidx.room.* <methods>;
}
