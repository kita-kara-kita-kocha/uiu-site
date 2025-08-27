import React, { useEffect } from 'react';

interface AgeVerificationModalProps {
  onVerify: (verified: boolean) => void;
}

const AgeVerificationModal: React.FC<AgeVerificationModalProps> = ({ onVerify }) => {
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    
    return () => {
      document.body.style.overflow = 'auto';
    };
  }, []);

  return (
    <div className="age-verification-modal show">
      <div className="age-verification-container">
        <div className="age-verification-header">
          <h2>🔞 年齢認証</h2>
          <p>このコンテンツは18歳以上のいうスキーを対象としています。</p>
        </div>
        <div className="age-verification-content">
          <p className="age-warning">
            このページにはいうちゃん好き好き大好きな成人向けのコンテンツが含まれている可能性があります。<br />
            18歳以上であることを確認してください。
          </p>
          <div className="age-verification-buttons">
            <button 
              className="age-verify-btn yes"
              onClick={() => onVerify(true)}
            >
              憂世いうが大好きです。<br />18歳以上です
            </button>
            <button 
              className="age-verify-btn no"
              onClick={() => onVerify(false)}
            >
              憂世いうが最推しです。<br />18歳になったらまた来ます
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgeVerificationModal;
