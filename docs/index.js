// DOM読み込み完了後に実行
document.addEventListener('DOMContentLoaded', function() {
    const thumbnailItems = document.querySelectorAll('.thumbnail-item');
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // フィルタ状態を管理するオブジェクト
    const filterState = {
        youtube: {
            subscriberOnly: false
        }
    };
    
    // 年齢認証状態を管理
    let ageVerified = false;
    
    // 年齢認証モーダルを表示する関数
    function showAgeVerificationModal() {
        const modal = document.getElementById('ageVerificationModal');
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
    
    // 年齢認証モーダルを非表示にする関数
    function hideAgeVerificationModal() {
        const modal = document.getElementById('ageVerificationModal');
        modal.classList.remove('show');
        document.body.style.overflow = 'auto';
    }
    
    // 年齢認証イベントリスナーを設定
    function setupAgeVerification() {
        const ageVerifyYes = document.getElementById('ageVerifyYes');
        const ageVerifyNo = document.getElementById('ageVerifyNo');
        
        ageVerifyYes.addEventListener('click', function() {
            ageVerified = true;
            hideAgeVerificationModal();
            
            // 裏垢タブを正しくアクティブにする
            const secretButton = document.querySelector('[data-tab="secret_ac"]');
            const tabButtons = document.querySelectorAll('.tab-button');
            const tabContents = document.querySelectorAll('.tab-content');
            
            // すべてのタブボタンからactiveクラスを削除
            tabButtons.forEach(btn => btn.classList.remove('active'));
            // 裏垢タブボタンにactiveクラスを追加
            if (secretButton) {
                secretButton.classList.add('active');
            }
            
            // すべてのタブコンテンツを非表示
            tabContents.forEach(content => content.classList.remove('active'));
            // 裏垢タブコンテンツを表示
            const secretContent = document.getElementById('secret_ac');
            if (secretContent) {
                secretContent.classList.add('active');
            }
            
            // 裏垢タブのコンテンツを読み込み
            updateTabContent('secret_ac');
        });
        
        ageVerifyNo.addEventListener('click', function() {
            hideAgeVerificationModal();
            // 他のタブに戻る（YouTubeタブを選択）
            const youtubeButton = document.querySelector('[data-tab="youtube"]');
            if (youtubeButton) {
                youtubeButton.click();
            }
        });
    }
    
    // JSONデータ読み込み関数
    async function loadTabData(tabName) {
        try {
            const response = await fetch(`${tabName}.json`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error(`Error loading ${tabName}.json:`, error);
            return { items: [] };
        }
    }
    
    // 文字列をJavaScript内で安全に使用できるようにエスケープする関数
    function escapeForJS(str) {
        if (!str) return '';
        return str
            .replace(/\\/g, '\\\\')    // バックスラッシュをエスケープ
            .replace(/'/g, "\\'")      // シングルクォートをエスケープ
            .replace(/"/g, '\\"')      // ダブルクォートをエスケープ
            .replace(/\n/g, '\\n')     // 改行をエスケープ
            .replace(/\r/g, '\\r')     // キャリッジリターンをエスケープ
            .replace(/\t/g, '\\t')     // タブをエスケープ
            .replace(/\u2028/g, '\\u2028')  // ラインセパレーターをエスケープ
            .replace(/\u2029/g, '\\u2029'); // パラグラフセパレーターをエスケープ
    }

    // サムネイルHTMLを生成する関数
    function createThumbnailHTML(item, tabType) {
        let additionalClass = '';
        let playButton = '';


        
        let infoHTML = `<h3>${item.title}</h3>`;
        
        if (item.description) {
            infoHTML += `<p>${item.description}</p>`;
        }
        if (item.metadata) {
            item.metadata.forEach(meta => {
                infoHTML += `<p>${meta}</p>`;
            });
        }

        // YouTubeの場合
        if (tabType === 'youtube' && item.videoId) {
            additionalClass = 'youtube';       
            // timestampsが存在する場合のみjoinメソッドを使用
            const timestampsStr = item.timestamps && Array.isArray(item.timestamps) ? item.timestamps.join(', ') : '';
            
            // YouTube動画の再生ボタン（data属性を使用）
            playButton = `<button class="play-button" data-video-id="${item.videoId}" data-title="${item.title}" data-timestamps="${timestampsStr}"></button>`;
            
            // item.addAdditionalClassが0個以上あればadditionalClassを追加
            if (item.addAdditionalClass && item.addAdditionalClass.length > 0) {
                additionalClass += ' ' + item.addAdditionalClass.join(' ');
                // 'メンバー限定'が含まれている場合はplayButtonを空文字化
                if (item.addAdditionalClass.includes('subscriber_only')) {
                    playButton = '';
                }
            }
        }
        // ニコニコ生放送の場合
        if (tabType === 'niconico_l') {
            additionalClass = 'niconico_l';
            // タイムシフト期限が現在日時を超えている場合は、additionalClassに'timeshiftout'を追加
            let timeshiftLimitDate;
            let currentDate = new Date();
            const timeshiftMeta = item.metadata && item.metadata.find(meta => meta.startsWith('タイムシフト視聴期限:'));
            if (timeshiftMeta) {
                timeshiftLimitDate = new Date(timeshiftMeta.split('タイムシフト視聴期限: ')[1].trim());
                if (timeshiftLimitDate < currentDate || timeshiftMeta === 'タイムシフト視聴期限: 視聴不可' || timeshiftMeta === 'タイムシフト視聴期限: 不明') {
                    additionalClass += ' timeshiftout';
                }
            } else {
                // タイムシフト期限がない場合は、'timeshiftout'を追加
                additionalClass += ' timeshiftout';
            }
        }
        if (tabType === 'fciu') {
            additionalClass = 'fciu';
            // 視聴条件に応じてクラスを追加
            const viewingCondition = item.metadata && item.metadata.find(meta => meta.startsWith('視聴条件:'));
            if (viewingCondition) {
                const condition = viewingCondition.split('視聴条件: ')[1].trim();
                if (condition === '会員のみ') {
                    additionalClass += ' fciu-members-only';
                } else if (condition === '一部無料') {
                    additionalClass += ' fciu-partial-free';
                } else if (condition === '全編無料') {
                    additionalClass += ' fciu-full-free';
                }
            }
        }
        if (tabType === 'secret_ac') {
            additionalClass = 'secret_ac';
        }

        return `
            <div class="thumbnail-item ${additionalClass}" style="position: relative;">
                <img src="${item.image}" alt="${item.alt || item.title}" class="thumbnail-image">
                ${playButton}
                <div class="thumbnail-info">
                    ${infoHTML}
                </div>
            </div>
        `;
    }
    
    // アイテムをフィルタリングする関数
    function filterItems(items, tabType) {
        if (tabType !== 'youtube') {
            return items;
        }
        
        const filters = filterState.youtube;
        console.log('フィルタ状態:', filters.subscriberOnly);
        
        if (filters.subscriberOnly) {
            const filteredItems = items.filter(item => {
                const hasSubscriberOnly = item.addAdditionalClass && 
                       item.addAdditionalClass.includes('subscriber_only');
                console.log('アイテム:', item.title, 'subscriber_only:', hasSubscriberOnly);
                return hasSubscriberOnly;
            });
            console.log('フィルタ後のアイテム数:', filteredItems.length, '/ 全体:', items.length);
            return filteredItems;
        }
        
        return items;
    }
    
    // タブコンテンツを更新する関数
    async function updateTabContent(tabName) {
        const data = await loadTabData(tabName);
        const tabContent = document.getElementById(tabName);
        const thumbnailGrid = tabContent.querySelector('.thumbnail-grid');
        
        if (data.items && data.items.length > 0) {
            // フィルタリングを適用
            const filteredItems = filterItems(data.items, tabName);
            
            thumbnailGrid.innerHTML = filteredItems.map(item => 
                createThumbnailHTML(item, tabName)
            ).join('');
            
            // 新しく追加されたアイテムにもイベントリスナーを追加（フィルタリング後のデータを渡す）
            addThumbnailEventListeners(thumbnailGrid, filteredItems, tabName);
            
            // フィルタ結果の表示・非表示
            updateFilterVisibility(tabName, filteredItems.length, data.items.length);
        }
    }
    
    // サムネイルにイベントリスナーを追加
    function addThumbnailEventListeners(container, filteredItems, tabName) {
        const items = container.querySelectorAll('.thumbnail-item');
        items.forEach((item, index) => {
            // 再生ボタンのイベントリスナーを追加
            const playButton = item.querySelector('.play-button');
            if (playButton) {
                playButton.addEventListener('click', function(e) {
                    e.stopPropagation(); // 親のクリックイベントを防ぐ
                    
                    const videoId = this.dataset.videoId;
                    const title = this.dataset.title;
                    const timestamps = this.dataset.timestamps;
                    
                    if (videoId && title) {
                        openVideoModal(videoId, title, timestamps);
                    }
                });
            }
            
            item.addEventListener('click', function(e) {
                // 再生ボタンがクリックされた場合は処理しない
                if (e.target.classList.contains('play-button')) {
                    return;
                }
                
                const title = this.querySelector('h3').textContent;
                
                // フィルタリング後のデータから該当アイテムを取得
                if (filteredItems && filteredItems[index]) {
                    const itemData = filteredItems[index];
                    if (itemData && itemData.video_url) {
                        // video_urlがあれば新しいタブで開く
                        window.open(itemData.video_url, '_blank');
                    } else {
                        // video_urlがない場合は従来のアラート表示
                        const imageSrc = this.querySelector('.thumbnail-image').src;
                        alert(`URL情報がありません。バグです。\nタイトル: ${title}\n画像: ${imageSrc}`);
                    }
                } else {
                    // フィルタリング後のデータがない場合のフォールバック
                    const thumbnailGrid = this.closest('.thumbnail-grid');
                    const tabContent = thumbnailGrid.closest('.tab-content');
                    const tabId = tabContent.id;
                    
                    // JSONデータから該当アイテムを探す
                    loadTabData(tabId).then(data => {
                        if (data.items) {
                            const itemData = data.items[index];
                            if (itemData && itemData.video_url) {
                                // video_urlがあれば新しいタブで開く
                                window.open(itemData.video_url, '_blank');
                            } else {
                                // video_urlがない場合は従来のアラート表示
                                const imageSrc = this.querySelector('.thumbnail-image').src;
                                alert(`URL情報がありません。バグです。\nタイトル: ${title}\n画像: ${imageSrc}`);
                            }
                        }
                    });
                }
            });
            
            item.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-8px) scale(1.02)';
            });
            
            item.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });
            
            // アニメーション遅延を設定
            item.style.animationDelay = `${(index + 1) * 0.1}s`;
        });
    }
    
    // タブ切り替え機能
    tabButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const targetTab = this.getAttribute('data-tab');
            
            // 裏垢タブの場合は年齢認証をチェック
            if (targetTab === 'secret_ac' && !ageVerified) {
                showAgeVerificationModal();
                return; // 年齢認証が完了するまで処理を停止
            }
            
            // すべてのタブボタンからactiveクラスを削除
            tabButtons.forEach(btn => btn.classList.remove('active'));
            // クリックされたボタンにactiveクラスを追加
            this.classList.add('active');
            
            // すべてのタブコンテンツを非表示
            tabContents.forEach(content => content.classList.remove('active'));
            // 対象のタブコンテンツを表示
            document.getElementById(targetTab).classList.add('active');
            
            // タブコンテンツを更新
            await updateTabContent(targetTab);
        });
    });
    
    // 初期タブのデータを読み込み
    const activeTab = document.querySelector('.tab-button.active');
    if (activeTab) {
        const initialTab = activeTab.getAttribute('data-tab');
        updateTabContent(initialTab);
    }
    
    // フィルタイベントリスナーを設定
    function setupFilterEventListeners() {
        const subscriberOnlyFilter = document.getElementById('subscriberOnlyFilter');
        if (subscriberOnlyFilter) {
            subscriberOnlyFilter.addEventListener('change', function() {
                filterState.youtube.subscriberOnly = this.checked;
                // YouTubeタブがアクティブな場合のみ更新
                const activeTabContent = document.querySelector('.tab-content.active');
                if (activeTabContent && activeTabContent.id === 'youtube') {
                    updateTabContent('youtube');
                }
            });
        }
    }
    
    // フィルタ結果の表示・非表示を更新する関数
    function updateFilterVisibility(tabName, filteredCount, totalCount) {
        if (tabName === 'youtube') {
            const filterControls = document.getElementById('youtube-filters');
            if (filterControls) {
                // フィルタが有効で結果が少ない場合に情報を表示
                let infoElement = filterControls.querySelector('.filter-info');
                
                if (filterState.youtube.subscriberOnly) {
                    if (!infoElement) {
                        infoElement = document.createElement('div');
                        infoElement.className = 'filter-info';
                        filterControls.appendChild(infoElement);
                    }
                    infoElement.textContent = `${filteredCount}件のメンバー限定コンテンツを表示中 (全${totalCount}件)`;
                } else {
                    if (infoElement) {
                        infoElement.remove();
                    }
                }
            }
        }
    }
    
    // フィルタイベントリスナーを設定
    setupFilterEventListeners();
    
    // 年齢認証イベントリスナーを設定
    setupAgeVerification();
    
    // 各サムネイルにクリックイベントを追加（初期読み込み時のサムネイル用）
    thumbnailItems.forEach((item, index) => {
        item.addEventListener('click', function(e) {
            // 再生ボタンがクリックされた場合は処理しない
            if (e.target.classList.contains('play-button')) {
                return;
            }
            
            const title = this.querySelector('h3').textContent;
            const imageSrc = this.querySelector('.thumbnail-image').src;
            
            // 従来のアラート表示（初期HTMLのサムネイル用）
            alert(`クリックされました:\n${title}\n画像: ${imageSrc}`);
        });
        
        // ホバーエフェクトの強化
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // 画像の遅延読み込み効果（オプション）
    const images = document.querySelectorAll('.thumbnail-image');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.style.opacity = '1';
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => {
        img.style.opacity = '0';
        img.style.transition = 'opacity 0.5s ease';
        imageObserver.observe(img);
        
        // 画像読み込み完了時に表示
        img.addEventListener('load', function() {
            this.style.opacity = '1';
        });
    });
    
    // キーボードナビゲーション
    document.addEventListener('keydown', function(e) {
        const focusedElement = document.activeElement;
        const currentIndex = Array.from(thumbnailItems).indexOf(focusedElement);
        
        switch(e.key) {
            case 'ArrowRight':
                if (currentIndex >= 0 && currentIndex < thumbnailItems.length - 1) {
                    thumbnailItems[currentIndex + 1].focus();
                    e.preventDefault();
                }
                break;
            case 'ArrowLeft':
                if (currentIndex > 0) {
                    thumbnailItems[currentIndex - 1].focus();
                    e.preventDefault();
                }
                break;
            case 'Enter':
                if (currentIndex >= 0) {
                    thumbnailItems[currentIndex].click();
                    e.preventDefault();
                }
                break;
        }
    });
    
    // サムネイルをフォーカス可能にする
    thumbnailItems.forEach((item, index) => {
        item.setAttribute('tabindex', '0');
        item.setAttribute('role', 'button');
        item.setAttribute('aria-label', `サムネイル ${index + 1}: ${item.querySelector('h3').textContent}`);
    });
});

// YouTube動画モーダル関数
function openVideoModal(videoId, title, timestamps) {
    const modal = document.getElementById('videoModal');
    const iframe = document.getElementById('videoIframe');
    const titleElement = document.getElementById('videoTitle');
    
    // タイトルを設定
    titleElement.textContent = title;
    
    // YouTube埋め込みURLを設定（JavaScript API有効化）
    iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0&enablejsapi=1&origin=${window.location.origin}`;
    
    // モーダルを表示
    modal.classList.add('show');
    
    // スクロールを無効化
    document.body.style.overflow = 'hidden';

    // タイムスタンプがある場合は表示
    if (timestamps && timestamps.length > 0) {
        const timestampList = document.getElementById('videoTimestamps');
        timestampList.innerHTML = ''; // 既存のリストをクリア
        timestamps.split(',').forEach(timestamp => {
            const listItem = document.createElement('li');
            listItem.textContent = timestamp.trim();
            listItem.addEventListener('click', function() {
                // タイムスタンプクリック時の処理: 特定の時間にジャンプ
                // タイムスタンプ文字列から最初に現れる時間部分（例: 1:23, 12:34:56など）を抽出
                const match = timestamp.match(/([0-9]{1,2}:[0-9]{2}(?::[0-9]{2})?)/);
                const timeStr = match ? match[1] : timestamp.trim();
                const timeParts = timeStr.split(':').map(part => parseInt(part, 10));
                let seconds = 0;
                if (timeParts.length === 3) {
                    // HH:MM:SS 形式
                    seconds = timeParts[0] * 3600 + timeParts[1] * 60 + timeParts[2];
                }
                else if (timeParts.length === 2) {
                    // MM:SS 形式
                    seconds = timeParts[0] * 60 + timeParts[1];
                }
                else if (timeParts.length === 1) {
                    // SS 形式
                    seconds = timeParts[0];
                }
                
                // 新しいジャンプ関数を使用
                jumpToTime(iframe, seconds);
                
                // 視覚的フィードバック
                listItem.style.backgroundColor = '#4a9eff';
                listItem.style.color = 'white';
                listItem.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    listItem.style.backgroundColor = '';
                    listItem.style.color = '';
                    listItem.style.transform = '';
                }, 500);
            });
            timestampList.appendChild(listItem);
        });
    }
    else {
        const timestampList = document.getElementById('videoTimestamps');
        timestampList.innerHTML = '<li>タイムスタンプはありません。</li>';
    }
}

function closeVideoModal() {
    const modal = document.getElementById('videoModal');
    const iframe = document.getElementById('videoIframe');
    
    // 動画を停止
    iframe.src = '';
    
    // モーダルを非表示
    modal.classList.remove('show');
    
    // スクロールを有効化
    document.body.style.overflow = 'auto';
}

// ESCキーでモーダルを閉じる
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeVideoModal();
    }
});

// モーダル背景をクリックして閉じる
document.getElementById('videoModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeVideoModal();
    }
});

// YouTube Player API用の関数
function jumpToTime(iframe, seconds) {
    // 方法1: postMessage APIを使用
    try {
        iframe.contentWindow.postMessage(
            JSON.stringify({
                event: 'command',
                func: 'seekTo',
                args: [seconds, true]
            }), 
            '*'
        );
    } catch (e) {
        console.log('postMessage failed, trying URL reload method');
    }
    
    // 方法2: URL再読み込み（フォールバック）
    setTimeout(() => {
        const currentSrc = iframe.src;
        if (currentSrc) {
            const baseUrl = currentSrc.split('?')[0];
            const newSrc = `${baseUrl}?autoplay=1&rel=0&enablejsapi=1&origin=${window.location.origin}&start=${seconds}`;
            iframe.src = newSrc;
        }
    }, 100);
}

// ユーティリティ関数
function addThumbnail(imageSrc, title, description) {
    const grid = document.querySelector('.thumbnail-grid');
    const thumbnailItem = document.createElement('div');
    thumbnailItem.className = 'thumbnail-item';
    
    thumbnailItem.innerHTML = `
        <img src="${imageSrc}" alt="${title}" class="thumbnail-image">
        <div class="thumbnail-info">
            <h3>${title}</h3>
            <p>${description}</p>
        </div>
    `;
    
    grid.appendChild(thumbnailItem);
    
    // 新しく追加されたアイテムにもイベントリスナーを追加
    thumbnailItem.addEventListener('click', function() {
        alert(`クリックされました:\n${title}\n画像: ${imageSrc}`);
    });
}