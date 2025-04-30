import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';

const API_URL = 'http://127.0.0.1:5000/jobs';

function App() {
  const [jobs, setJobs] = useState([]);
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [form, setForm] = useState({ title: '', company: '', location: '', country: '' });
  const [filters, setFilters] = useState({ country: '', title: '', location: '' });

  useEffect(() => {
    fetchJobs();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [filters, jobs]);

  const fetchJobs = async () => {
    try {
      const response = await axios.get(API_URL);
      setJobs(response.data);
      setFilteredJobs(response.data);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  const handleInput = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const addJob = async () => {
    if (!form.title || !form.company || !form.location || !form.country) return;
    try {
      const response = await axios.post(API_URL, form);
      const updatedJobs = [...jobs, response.data];
      setJobs(updatedJobs);
      setForm({ title: '', company: '', location: '', country: '' });
    } catch (error) {
      console.error('Error adding job:', error);
    }
  };

  const deleteJob = async (id) => {
    try {
      await axios.delete(`${API_URL}/${id}`);
      const updatedJobs = jobs.filter((job) => job.id !== id);
      setJobs(updatedJobs);
    } catch (error) {
      console.error('Error deleting job:', error);
    }
  };

  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const applyFilters = () => {
    let result = [...jobs];
    if (filters.country) {
      result = result.filter(job =>
        job.country.toLowerCase().includes(filters.country.toLowerCase())
      );
    }
    if (filters.title) {
      result = result.filter(job =>
        job.title.toLowerCase().includes(filters.title.toLowerCase())
      );
    }
    if (filters.location) {
      result = result.filter(job =>
        job.location.toLowerCase().includes(filters.location.toLowerCase())
      );
    }
    setFilteredJobs(result);
  };

  return (
    <div className="flex p-6 max-w-7xl mx-auto gap-6">
      {/* Sidebar Filters */}
      <div className="w-64 bg-gray-50 p-4 rounded-2xl shadow-md border">
        <h2 className="text-xl font-bold mb-4">Filters</h2>
        <input
          name="country"
          placeholder="Filter by Country"
          value={filters.country}
          onChange={handleFilterChange}
          className="border p-2 rounded w-full mb-3"
        />
        <input
          name="title"
          placeholder="Filter by Title"
          value={filters.title}
          onChange={handleFilterChange}
          className="border p-2 rounded w-full mb-3"
        />
        <input
          name="location"
          placeholder="Filter by Location"
          value={filters.location}
          onChange={handleFilterChange}
          className="border p-2 rounded w-full"
        />
      </div>

      {/* Main Content */}
      <div className="flex-1">
        <h1 className="text-3xl font-bold mb-6 text-center">Job Listings</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {['title', 'company', 'location', 'country'].map((field) => (
            <input
              key={field}
              name={field}
              placeholder={`Add ${field[0].toUpperCase() + field.slice(1)}`}
              value={form[field]}
              onChange={handleInput}
              className="border p-2 rounded w-full"
            />
          ))}
          <button
            onClick={addJob}
            className="col-span-1 md:col-span-2 bg-blue-600 text-white p-2 rounded hover:bg-blue-700 transition"
          >
            Add Job
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredJobs.map((job) => (
            <motion.div
              key={job.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              layout
              className="bg-white p-4 rounded-2xl shadow-md border border-gray-200"
            >
              <h2 className="text-xl font-semibold">{job.title}</h2>
              <p className="text-sm text-gray-600">{job.company}</p>
              <p className="text-sm text-gray-600">{job.location}, {job.country}</p>
              <p className="text-xs text-gray-400 mt-1">Scraped at: {job.scraped_at}</p>
              <button
                onClick={() => deleteJob(job.id)}
                className="mt-3 bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600 transition"
              >
                Delete
              </button>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
