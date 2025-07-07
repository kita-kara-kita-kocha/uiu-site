// DOM読み込み完了後に実行
document.addEventListener('DOMContentLoaded', function() {
    const thumbnailItems = document.querySelectorAll('.thumbnail-item');
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
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
    
    // サムネイルHTMLを生成する関数
    function createThumbnailHTML(item, tabType) {
        let additionalClass = '';
        if (tabType === 'niconico_l') additionalClass = 'niconico_l';
        else if (tabType === 'niconico_v') additionalClass = 'niconico_v';
        else if (tabType === 'fciu') additionalClass = 'fciu';
        else if (tabType === 'secret_ac') additionalClass = 'secret_ac';
        else if (item.special) additionalClass = item.special;
        
        let infoHTML = `<h3>${item.title}</h3>`;
        
        if (item.description) {
            infoHTML += `<p>${item.description}</p>`;
        }
        
        if (item.metadata) {
            item.metadata.forEach(meta => {
                infoHTML += `<p>${meta}</p>`;
            });
        }

        // YouTubeの場合のみ再生ボタンを追加
        let playButton = '';
        if (tabType === 'youtube' && item.videoId) {
            // YouTube動画の再生ボタン
            playButton = `<button class="play-button" onclick="openVideoModal('${item.videoId}', '${item.title.replace(/'/g, "\\'")}')"></button>`;
            // timestamp表示ボタン
            timestampButton = `<button class="timestamp-button" onclick="openTimestampModal('${item.videoId}', '${item.timestamps.join(', ')}')">Timestamp</button>`;
        }
        
        return `
            <div class="thumbnail-item ${additionalClass}" style="position: relative;">
                <img src="${item.image}" alt="${item.alt || item.title}" class="thumbnail-image">
                ${playButton}
                <div class="thumbnail-info">
                    ${infoHTML}
                </div>
                ${timestamp_dev}
            </div>
        `;
    }
    
    // タブコンテンツを更新する関数
    async function updateTabContent(tabName) {
        const data = await loadTabData(tabName);
        const tabContent = document.getElementById(tabName);
        const thumbnailGrid = tabContent.querySelector('.thumbnail-grid');
        
        if (data.items && data.items.length > 0) {
            thumbnailGrid.innerHTML = data.items.map(item => 
                createThumbnailHTML(item, tabName)
            ).join('');
            
            // 新しく追加されたアイテムにもイベントリスナーを追加
            addThumbnailEventListeners(thumbnailGrid);
        }
    }
    
    // サムネイルにイベントリスナーを追加
    function addThumbnailEventListeners(container) {
        const items = container.querySelectorAll('.thumbnail-item');
        items.forEach((item, index) => {
            item.addEventListener('click', function(e) {
                // 再生ボタンがクリックされた場合は処理しない
                if (e.target.classList.contains('play-button')) {
                    return;
                }
                
                const title = this.querySelector('h3').textContent;
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
function openVideoModal(videoId, title) {
    const modal = document.getElementById('videoModal');
    const iframe = document.getElementById('videoIframe');
    const titleElement = document.getElementById('videoTitle');
    
    // タイトルを設定
    titleElement.textContent = title;
    
    // YouTube埋め込みURLを設定
    iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`;
    
    // モーダルを表示
    modal.classList.add('show');
    
    // スクロールを無効化
    document.body.style.overflow = 'hidden';
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