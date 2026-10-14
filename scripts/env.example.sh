# Source in the current shell; substitute your own SDK paths.
export ANDROID_HOME="${ANDROID_HOME:-$HOME/Library/Android/sdk}"
export PATH="$PWD/.local/flutter/bin:$PWD/.work/tools/maestro/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"
# Select a JDK compatible with your pinned Gradle version. The reference host
# uses JDK 17 for Compose/RN and Android Studio's JDK 25 for Flutter.
# export JAVA_HOME="/path/to/jdk-17"
export MAESTRO_CLI_NO_ANALYTICS=1
export MAESTRO_CLI_ANALYSIS_NOTIFICATION_DISABLED=true
