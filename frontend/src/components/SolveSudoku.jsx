import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dropzone from 'react-dropzone';
import { Link } from 'react-router-dom'; 
import { sudoku } from '../assets'; 
import Loader from './Loader';

const SolveSudoku = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState();
  const [data, setData] = useState();
  const [image, setImage] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [outputImage, setOutputImage] = useState(null); // State to hold the output image

  const sendFile = async () => {
    if (image) {
      let formData = new FormData();
      formData.append("file", selectedFile);
      try {
        let res = await axios.post("http://localhost:8080/solve", formData, {
          responseType: 'arraybuffer' 
        });
        const imageBlob = new Blob([res.data], { type: 'image/jpeg' }); 
        setOutputImage(URL.createObjectURL(imageBlob)); // Set the output image URL
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching image:', error);
        setIsLoading(false);
      }
    }
  }

  const clearData = () => {
    setData(null);
    setImage(false);
    setSelectedFile(null);
    setPreview(null);
    setOutputImage(null); 
  };

  useEffect(() => {
    if (!selectedFile) {
      setPreview(undefined);
      return;
    }
    const objectUrl = URL.createObjectURL(selectedFile);
    setPreview(objectUrl);
  }, [selectedFile]);

  useEffect(() => {
    if (!preview) {
      return;
    }
    setIsLoading(true);
    sendFile();
  }, [preview]);

  const onSelectFile = (files) => {
    if (!files || files.length === 0) {
      setSelectedFile(undefined);
      setImage(false);
      setData(undefined);
      return;
    }
    setSelectedFile(files[0]);
    setData(undefined);
    setImage(true);
  };

  return (
    <div className="gradient">
      <header className="main:after px-12 py-12">
        <Link to="/" className='flex gap-2 flex-center'>
            <img src={sudoku} alt="Logo" className="w-10 h-10 rounded" />
            <h1 className="text-black text-2xl font-mono font-bold ml-2">SudokuSolver</h1>
        </Link>
      </header>

      <main className="main:after">
        <div className="mb-8 text-center w-full">
          <p className="text-3xl font-mono">Navigate Sudoku grids like a pro.</p>
        </div>
        
        <div className={`rounded-lg ml-60 mr-60 items-center ${!image ? 'border-2 border-dashed border-gray-400' : ''}`}>
          {!image && (
            <div className="p-4">
              <Dropzone onDrop={acceptedFiles => onSelectFile(acceptedFiles)}>
                {({ getRootProps, getInputProps }) => (
                  <div {...getRootProps()} className="border-2 border-dashed border-gray-400 p-4 text-center cursor-pointer">
                    <input {...getInputProps()} />
                    <p>Drop your sudoku puzzle here and witness the magic!!</p>
                  </div>
                )}
              </Dropzone>
            </div>
          )}

          {image && (
            <div className="flex justify-between w-full">
              <div className="w-1/2 p-4">
                <img src={preview} alt="Input" className="object-cover w-full h-full" />
              </div>
              <div className="w-1/2 p-4">
                {outputImage && (
                  <img src={outputImage} alt="Output" className="object-cover w-full h-full" />
                )}
                {isLoading && (
                  <div className="flex flex-col items-center justify-center">
                    <Loader />
                    <p className="mt-2 text-xl">Processing</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <button
            onClick={clearData}
            className="mt-4 mx-auto flex items-center justify-center px-6 py-2 bg-red-500 text-black rounded-lg hover:bg-red-600"
        >
            Clear
        </button>

      </main>
    </div>
  );
};

export default SolveSudoku;
