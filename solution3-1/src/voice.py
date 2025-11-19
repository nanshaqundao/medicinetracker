"""
语音识别JavaScript代码模块
包含Web Speech API相关的JavaScript代码
"""

# 语音识别JavaScript代码
VOICE_RECOGNITION_JS = """
<script>
// 全局变量
window.voiceRecognition = null;
window.isContinuousMode = false;
window.isListening = false;

// 单次语音识别
window.startVoiceRecognition = function() {
    return new Promise((resolve, reject) => {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('❌ 浏览器不支持语音识别\\n请使用Chrome或Edge浏览器');
            reject('not supported');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'zh-CN';

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            console.log('✅ Voice recognized:', transcript);
            resolve(transcript);
        };

        recognition.onerror = function(event) {
            console.error('Voice error:', event.error);
            if (event.error === 'not-allowed') {
                alert('❌ 麦克风权限被拒绝\\n请在浏览器设置中允许麦克风访问');
            }
            reject(event.error);
        };

        try {
            recognition.start();
            console.log('🎤 Single voice recognition started');
        } catch (e) {
            console.error('Failed to start:', e);
            reject(e);
        }
    });
};

// 连续语音识别
window.startContinuousVoice = function() {
    console.log('Starting continuous mode...');

    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert('❌ 浏览器不支持语音识别\\n请使用Chrome或Edge浏览器');
        return 'error';
    }

    if (window.isListening) {
        // 停止
        window.isContinuousMode = false;
        window.isListening = false;
        if (window.voiceRecognition) {
            window.voiceRecognition.stop();
        }
        console.log('🛑 Continuous mode stopped');
        return 'stopped';
    }

    // 启动连续模式
    window.isContinuousMode = true;
    window.isListening = true;
    window.isRestarting = false;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    window.voiceRecognition = new SpeechRecognition();
    window.voiceRecognition.continuous = false;
    window.voiceRecognition.interimResults = false;
    window.voiceRecognition.lang = 'zh-CN';

    // 统一的重启函数
    window.restartRecognition = function() {
        if (!window.isContinuousMode || !window.isListening) {
            console.log('❌ Not in continuous mode, skipping restart');
            return;
        }

        if (window.isRestarting) {
            console.log('⏳ Already restarting, skipping...');
            return;
        }

        window.isRestarting = true;
        console.log('🔄 Scheduling restart...');

        setTimeout(() => {
            if (window.isContinuousMode && window.isListening) {
                try {
                    window.voiceRecognition.start();
                    console.log('✅ Recognition restarted');
                } catch (e) {
                    console.error('❌ Restart failed:', e);
                    window.isRestarting = false;
                }
            } else {
                console.log('❌ Mode changed, not restarting');
                window.isRestarting = false;
            }
        }, 500);
    };

    window.voiceRecognition.onstart = function() {
        console.log('🎤 Recognition started');
        window.isRestarting = false;
    };

    window.voiceRecognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        console.log('✅ Voice recognized:', transcript);

        // 触发添加
        setTimeout(() => {
            const textbox = document.querySelector('textarea[placeholder*="语音输入"]');
            const addBtn = Array.from(document.querySelectorAll('button')).find(
                btn => btn.textContent.includes('添加到列表')
            );

            if (textbox && addBtn) {
                textbox.value = transcript;
                textbox.dispatchEvent(new Event('input', { bubbles: true }));
                setTimeout(() => addBtn.click(), 100);
            }
        }, 100);
    };

    window.voiceRecognition.onerror = function(event) {
        console.log('⚠️ Voice error:', event.error);

        if (event.error === 'not-allowed') {
            alert('❌ 麦克风权限被拒绝');
            window.isListening = false;
            window.isContinuousMode = false;
            window.isRestarting = false;
        } else if (event.error === 'aborted') {
            console.log('⏹️ User stopped');
            window.isRestarting = false;
        }
    };

    window.voiceRecognition.onend = function() {
        console.log('🏁 Recognition ended');

        if (window.isContinuousMode && window.isListening) {
            window.restartRecognition();
        } else {
            console.log('❌ Continuous mode off, not restarting');
            window.isRestarting = false;
        }
    };

    try {
        window.voiceRecognition.start();
        console.log('🎤 Continuous mode started');
        return 'started';
    } catch (e) {
        console.error('Failed to start:', e);
        window.isListening = false;
        window.isContinuousMode = false;
        window.isRestarting = false;
        return 'error';
    }
};
</script>
"""
