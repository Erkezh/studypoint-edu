import React, { useState, useEffect, useCallback } from 'react';

// Exercise ID for parent communication
const EXERCISE_ID = 'kazakh-rectangle-area';

// Helper function to send messages to parent window
const sendMessageToParent = (data: {
  id: string;
  correctAnswer: string;
  studentAnswer: string;
  isCorrect: boolean;
}) => {
  if (window.parent && window.parent !== window) {
    window.parent.postMessage(data, '*');
  }
  // Also log to console for debugging
  console.log('[Exercise Result]', data);
};

const KazakhRectangleAreaApp = () => {
  const [currentQuestion, setCurrentQuestion] = useState(1);
  const [targetArea, setTargetArea] = useState(12);
  const [selectedCells, setSelectedCells] = useState(new Set());
  const [showAnswer, setShowAnswer] = useState(false);
  const [isCorrect, setIsCorrect] = useState(null);
  const [score, setScore] = useState(0);
  const [attempts, setAttempts] = useState(0);
  const [correctAnswers, setCorrectAnswers] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState(null);

  const gridSize = 10;

  // Generate possible rectangle dimensions for a given area
  const getFactorPairs = (area) => {
    const pairs = [];
    for (let i = 1; i <= Math.sqrt(area); i++) {
      if (area % i === 0) {
        const width = i;
        const height = area / i;
        if (width <= gridSize && height <= gridSize) {
          pairs.push([width, height]);
        }
      }
    }
    return pairs;
  };

  // Format correct answer as string for message
  const formatCorrectAnswer = (area) => {
    const pairs = getFactorPairs(area);
    const dimensions = pairs.map(([w, h]) => `${w}×${h}`).join(' немесе ');
    return `${area} шаршы бірлік (${dimensions})`;
  };

  // Format student answer as string for message
  const formatStudentAnswer = (cells) => {
    if (cells.size === 0) return 'Таңдалмаған';
    
    const cellsArray = Array.from(cells).map(id => {
      const [row, col] = id.split('-').map(Number);
      return { row, col };
    });
    
    const minRow = Math.min(...cellsArray.map(c => c.row));
    const maxRow = Math.max(...cellsArray.map(c => c.row));
    const minCol = Math.min(...cellsArray.map(c => c.col));
    const maxCol = Math.max(...cellsArray.map(c => c.col));
    
    const width = maxCol - minCol + 1;
    const height = maxRow - minRow + 1;
    
    return `${cells.size} шаршы бірлік (${width}×${height})`;
  };

  // Generate correct answer examples
  const generateCorrectAnswers = (area) => {
    const pairs = getFactorPairs(area);
    const answers = [];
    
    pairs.forEach(([width, height]) => {
      const positions = [
        { startRow: 1, startCol: 1 },
        { startRow: 2, startCol: 3 },
        { startRow: 0, startCol: 5 }
      ];
      
      positions.forEach(pos => {
        if (pos.startRow + height <= gridSize && pos.startCol + width <= gridSize) {
          const cells = new Set();
          for (let r = pos.startRow; r < pos.startRow + height; r++) {
            for (let c = pos.startCol; c < pos.startCol + width; c++) {
              cells.add(`${r}-${c}`);
            }
          }
          answers.push({ cells, width, height });
        }
      });
    });
    
    return answers.slice(0, 3);
  };

  // Generate a random area that has reasonable factor pairs
  const generateRandomArea = () => {
    const possibleAreas = [];
    for (let area = 6; area <= 90; area++) {
      const pairs = getFactorPairs(area);
      if (pairs.length > 0) {
        possibleAreas.push(area);
      }
    }
    return possibleAreas[Math.floor(Math.random() * possibleAreas.length)];
  };

  useEffect(() => {
    const newArea = generateRandomArea();
    setTargetArea(newArea);
    setSelectedCells(new Set());
    setShowAnswer(false);
    setIsCorrect(null);
    setIsDragging(false);
    setDragStart(null);
    setCorrectAnswers(generateCorrectAnswers(newArea));
  }, [currentQuestion]);

  // Calculate the rectangle area between two points
  const getRectangleCells = (startRow, startCol, endRow, endCol) => {
    const minRow = Math.min(startRow, endRow);
    const maxRow = Math.max(startRow, endRow);
    const minCol = Math.min(startCol, endCol);
    const maxCol = Math.max(startCol, endCol);
    
    const cells = new Set();
    for (let r = minRow; r <= maxRow; r++) {
      for (let c = minCol; c <= maxCol; c++) {
        cells.add(`${r}-${c}`);
      }
    }
    return cells;
  };

  const handleMouseDown = (row, col) => {
    if (showAnswer) return;
    
    setIsDragging(true);
    setDragStart({ row, col });
    setSelectedCells(new Set([`${row}-${col}`]));
  };

  const handleMouseEnter = (row, col) => {
    if (!isDragging || !dragStart || showAnswer) return;
    
    const rectangleCells = getRectangleCells(
      dragStart.row, dragStart.col,
      row, col
    );
    setSelectedCells(rectangleCells);
  };

  const handleMouseUp = () => {
    if (isDragging) {
      setIsDragging(false);
    }
  };

  // Add global mouse up listener
  useEffect(() => {
    const handleGlobalMouseUp = () => {
      if (isDragging) {
        setIsDragging(false);
      }
    };
    
    document.addEventListener('mouseup', handleGlobalMouseUp);
    return () => {
      document.removeEventListener('mouseup', handleGlobalMouseUp);
    };
  }, [isDragging]);

  const isValidRectangle = useCallback(() => {
    if (selectedCells.size === 0) return false;
    
    const cells = Array.from(selectedCells).map(id => {
      const [row, col] = id.split('-').map(Number);
      return { row, col };
    });
    
    const minRow = Math.min(...cells.map(c => c.row));
    const maxRow = Math.max(...cells.map(c => c.row));
    const minCol = Math.min(...cells.map(c => c.col));
    const maxCol = Math.max(...cells.map(c => c.col));
    
    const expectedCells = (maxRow - minRow + 1) * (maxCol - minCol + 1);
    
    if (expectedCells !== selectedCells.size) return false;
    
    for (let r = minRow; r <= maxRow; r++) {
      for (let c = minCol; c <= maxCol; c++) {
        if (!selectedCells.has(`${r}-${c}`)) {
          return false;
        }
      }
    }
    
    return true;
  }, [selectedCells]);

  const checkAnswer = () => {
    const selectedArea = selectedCells.size;
    const correct = selectedArea === targetArea && isValidRectangle();
    
    setIsCorrect(correct);
    setShowAnswer(true);
    setAttempts(attempts + 1);
    
    // Send message to parent window - используем формат exercise-result для совместимости с PracticeSession
    const messageData = {
      type: 'exercise-result',
      id: `${EXERCISE_ID}-q${currentQuestion}`,
      correctAnswer: formatCorrectAnswer(targetArea),
      studentAnswer: formatStudentAnswer(selectedCells),
      isCorrect: correct
    };
    
    // Отправляем сообщение родительскому окну (PracticeSession)
    if (window.parent && window.parent !== window) {
      window.parent.postMessage(messageData, '*');
    }
    console.log('[Exercise Result]', messageData);
    
    // НЕ переходим автоматически к следующему вопросу - это делает PracticeSession
    // if (correct) {
    //   setScore(score + 1);
    //   setTimeout(() => {
    //     nextQuestion();
    //   }, 1500);
    // }
  };

  const nextQuestion = () => {
    setCurrentQuestion(currentQuestion + 1);
  };

  const resetGrid = () => {
    setSelectedCells(new Set());
    setShowAnswer(false);
    setIsCorrect(null);
    setIsDragging(false);
    setDragStart(null);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-indigo-800 mb-2">
          Берілген аудандағы тікбұрышты бояу
        </h1>
      </div>

      {/* Stats */}
      <div className="flex justify-center gap-6 mb-6">
      </div>

      {/* Question */}
      <div className="bg-white rounded-lg p-6 shadow-lg mb-6">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            <span className="text-2xl font-bold text-blue-600">{targetArea}</span> шаршы бірлік.
          </h2>
          <p className="text-gray-600">
            Тышқанды басып ұстап, тікбұрыш сызыңыз
          </p>
        </div>
      </div>

      {/* Grid */}
      <div className="flex justify-center mb-6">
        <div 
          className="inline-block border-2 border-gray-400 bg-white rounded-lg p-4 select-none"
          onMouseLeave={() => setIsDragging(false)}
        >
          <div className="grid grid-cols-10 gap-1">
            {Array.from({ length: gridSize }, (_, row) =>
              Array.from({ length: gridSize }, (_, col) => {
                const cellId = `${row}-${col}`;
                const isSelected = selectedCells.has(cellId);
                const isInCorrectAnswer = showAnswer && correctAnswers.some(answer => 
                  answer.cells.has(cellId)
                );
                
                // Определяем классы для ячейки
                let cellClassName = 'w-8 h-8 border border-gray-300 transition-all duration-100 ';
                cellClassName += isDragging ? 'cursor-crosshair' : 'cursor-pointer';
                cellClassName += ' ';
                
                if (isSelected) {
                  if (isCorrect === true) {
                    cellClassName += 'bg-green-400';
                  } else if (isCorrect === false) {
                    cellClassName += 'bg-red-400';
                  } else {
                    cellClassName += 'bg-blue-400';
                  }
                } else if (isInCorrectAnswer && showAnswer) {
                  cellClassName += 'bg-green-200';
                } else {
                  cellClassName += 'bg-white hover:bg-gray-100';
                }
                
                return (
                  <div
                    key={cellId}
                    className={cellClassName}
                    onMouseDown={() => handleMouseDown(row, col)}
                    onMouseEnter={() => handleMouseEnter(row, col)}
                    onMouseUp={handleMouseUp}
                    style={{ userSelect: 'none' }}
                  />
                );
              })
            )}
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex justify-center gap-4 mb-6">
        <button
          onClick={resetGrid}
          className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
          disabled={showAnswer}
        >
          Тазалау
        </button>
        <button
          onClick={checkAnswer}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          disabled={showAnswer || selectedCells.size === 0}
        >
          Тексеру
        </button>
        {showAnswer && (
          <button
            onClick={nextQuestion}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            Келесі сұрақ
          </button>
        )}
      </div>

      {/* Current Selection Info */}
      {selectedCells.size > 0 && !showAnswer && (
        <div className="text-center mb-4">
          <div className="bg-white rounded-lg p-3 shadow-md inline-block">
            <span className="text-gray-600">Таңдалған аудан: </span>
            <span className="font-bold text-blue-600">{selectedCells.size}</span>
            <span className="text-gray-600"> шаршы бірлік</span>
          </div>
        </div>
      )}

      {/* Feedback */}
      {showAnswer && (
        <div className="bg-white rounded-lg p-6 shadow-lg">
          <div className="text-center mb-4">
            {isCorrect ? (
              <div className="text-green-600">
                <div className="text-2xl font-bold mb-2">Дұрыс!</div>
                <p>Сіз {targetArea} шаршы бірлік аудандағы тікбұрышты дұрыс бойадыңыз.</p>
              </div>
            ) : (
              <div className="text-red-600">
                <div className="text-2xl font-bold mb-2">Қате</div>
                <p>
                  Сіз {selectedCells.size} ұяшық таңдадыңыз, бірақ {targetArea} қажет.
                  {!isValidRectangle() && selectedCells.size === targetArea && " Тікбұрыш пішіні болуы керек."}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="mt-8 bg-white rounded-lg p-4 shadow-md">
        <h3 className="font-semibold text-gray-700 mb-2">Нұсқаулық:</h3>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• Тышқанды басып ұстап, тікбұрыш пішінін сызыңыз</li>
          <li>• Бастапқы нүктеден ағымдағы орынға дейін барлық ұяшықтар автоматты түрде боялады</li>
          <li>• Тікбұрыштың ауданы көрсетілген санға тең болуы керек</li>
          <li>• Әртүрлі өлшемдегі тікбұрыштар жасауға болады (мысалы: 2×6 = 3×4 = 12)</li>
          <li>• Жасыл түс - дұрыс жауап, қызыл түс - қате жауап</li>
        </ul>
      </div>
    </div>
  );
};

export default KazakhRectangleAreaApp;
