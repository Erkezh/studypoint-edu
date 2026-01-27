import React, { useState, useEffect } from 'react';
import { RefreshCw, Check, X } from 'lucide-react';

const FractionComparison = () => {
  const [problems, setProblems] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [userAnswer, setUserAnswer] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const [score, setScore] = useState(0);

  const generateFraction = () => {
    const isMixed = Math.random() > 0.3;
    if (isMixed) {
      const whole = Math.floor(Math.random() * 2) + 1;
      const numerator = Math.floor(Math.random() * 7) + 1;
      const denominator = Math.floor(Math.random() * 7) + 2;
      return { whole, numerator, denominator, isMixed: true };
    } else {
      const numerator = Math.floor(Math.random() * 15) + 1;
      const denominator = Math.floor(Math.random() * 15) + 2;
      return { whole: 0, numerator, denominator, isMixed: false };
    }
  };

  const fractionToDecimal = (frac) => {
    return frac.whole + (frac.numerator / frac.denominator);
  };

  const getCorrectAnswer = (frac1, frac2) => {
    const val1 = fractionToDecimal(frac1);
    const val2 = fractionToDecimal(frac2);
    if (Math.abs(val1 - val2) < 0.001) return '=';
    return val1 > val2 ? '>' : '<';
  };

  const generateProblems = () => {
    const newProblems = [];
    for (let i = 0; i < 8; i++) {
      const frac1 = generateFraction();
      const frac2 = generateFraction();
      const correctAnswer = getCorrectAnswer(frac1, frac2);
      newProblems.push({ id: i, frac1, frac2, correctAnswer });
    }
    setProblems(newProblems);
    setCurrentIndex(0);
    setUserAnswer(null);
    setShowResult(false);
    setScore(0);
  };

  useEffect(() => {
    generateProblems();
  }, []);

  const handleAnswerSelect = (value) => {
    setUserAnswer(value);
  };

  const handleSubmit = () => {
    if (!userAnswer) return;
    setShowResult(true);
    if (userAnswer === problems[currentIndex].correctAnswer) {
      setScore(score + 1);
    }
  };

  const handleNext = () => {
    if (currentIndex < problems.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setUserAnswer(null);
      setShowResult(false);
    } else {
      // Quiz complete
      setShowResult(true);
    }
  };

  const currentProblem = problems[currentIndex];

  const FractionDisplay = ({ frac }) => {
    if (frac.isMixed && frac.whole > 0) {
      return (
        <div className="flex items-center gap-1">
          <span className="text-2xl font-semibold">{frac.whole}</span>
          <div className="flex flex-col items-center">
            <span className="text-lg border-b border-gray-800 px-1">{frac.numerator}</span>
            <span className="text-lg px-1">{frac.denominator}</span>
          </div>
        </div>
      );
    }
    return (
      <div className="flex flex-col items-center">
        <span className="text-lg border-b border-gray-800 px-2">{frac.numerator}</span>
        <span className="text-lg px-2">{frac.denominator}</span>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-indigo-900">
              Comparing Mixed Numbers & Fractions
            </h1>
          </div>

          {problems.length > 0 && currentIndex < problems.length && (
            <>
              <div className="border-2 border-gray-300 rounded-lg p-8 mb-8 bg-white">
                <div className="flex items-center justify-center gap-8">
                  <FractionDisplay frac={currentProblem.frac1} />

                  <div className="flex gap-3">
                    {['<', '=', '>'].map(symbol => (
                      <button
                        key={symbol}
                        onClick={() => handleAnswerSelect(symbol)}
                        disabled={showResult}
                        className={`w-16 h-16 rounded-lg border-2 text-2xl font-bold transition ${
                          userAnswer === symbol
                            ? 'bg-indigo-600 text-white border-indigo-600'
                            : 'bg-white border-gray-300 hover:border-indigo-400 hover:bg-indigo-50'
                        } ${showResult ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}`}
                      >
                        {symbol}
                      </button>
                    ))}
                  </div>

                  <FractionDisplay frac={currentProblem.frac2} />
                </div>

                {showResult && (
                  <div className="mt-6 text-center">
                    {userAnswer === currentProblem.correctAnswer ? (
                      <div className="flex items-center justify-center gap-2 text-green-600 text-xl font-semibold">
                        <Check size={28} />
                        Correct!
                      </div>
                    ) : (
                      <div className="flex flex-col items-center gap-2 text-red-600 text-xl font-semibold">
                        <div className="flex items-center gap-2">
                          <X size={28} />
                          Incorrect
                        </div>
                        <div className="text-gray-700">
                          The correct answer is: {currentProblem.correctAnswer}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              <div className="flex justify-end items-center">
                {!showResult && (
                  <button
                    onClick={handleSubmit}
                    disabled={!userAnswer}
                    className={`px-6 py-3 rounded-lg transition text-lg font-semibold ${
                      userAnswer
                        ? 'bg-green-600 text-white hover:bg-green-700 cursor-pointer'
                        : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    }`}
                  >
                    Submit
                  </button>
                )}

                {showResult && currentIndex < problems.length - 1 && (
                  <button
                    onClick={handleNext}
                    className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition text-lg font-semibold"
                  >
                    Next Question
                  </button>
                )}

                {showResult && currentIndex === problems.length - 1 && (
                  <button
                    onClick={generateProblems}
                    className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition text-lg font-semibold"
                  >
                    Try Again
                  </button>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default FractionComparison;