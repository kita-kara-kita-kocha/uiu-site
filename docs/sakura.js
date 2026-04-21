window.addEventListener('DOMContentLoaded', () => {
  // 現在の月を取得（0ベースなので、3月=2, 4月=3）
  const currentMonth = new Date().getMonth();
  
  // 3月（2）または4月（3）の場合のみ桜のアニメーションを実行
  if (currentMonth === 2 || currentMonth === 3) {
    // コンテナを指定
    const section = document.querySelector('.container');

    // 花びらを生成する関数
    const createPetal = () => {
      const petalEl = document.createElement('span');
      petalEl.className = 'petal';
      const minSize = 10;
      const maxSize = 15;
      const size = Math.random() * (maxSize + 1 - minSize) + minSize;
      petalEl.style.width = `${size}px`;
      petalEl.style.height = `${size}px`;
      petalEl.style.left = Math.random() * innerWidth + 'px';
      section.appendChild(petalEl);

      // 一定時間が経てば花びらを消す
      setTimeout(() => {
        petalEl.remove();
      }, 10000);
    }

    // 花びらを生成する間隔をミリ秒で指定
    setInterval(createPetal, 300);
  }
});