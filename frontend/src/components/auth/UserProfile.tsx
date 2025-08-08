import React, { useState, useEffect } from 'react';
import { useUser } from '../../contexts/UserContext';
import { authService } from '../../services';
import type { UpdateProfileRequest, ChangePasswordRequest } from '../../services/authService';

interface ProfileFormData {
  first_name: string;
  last_name: string;
  profile: {
    phone: string;
    location: string;
    bio: string;
    experience_years: number;
    skills: string[];
  };
}

interface PasswordFormData {
  old_password: string;
  new_password: string;
  new_password_confirm: string;
}

interface FormErrors {
  [key: string]: string;
}

export const UserProfile: React.FC = () => {
  const { state, updateUser, setLoading, setError } = useUser();
  const [activeTab, setActiveTab] = useState<'profile' | 'password'>('profile');
  const [profileData, setProfileData] = useState<ProfileFormData>({
    first_name: '',
    last_name: '',
    profile: {
      phone: '',
      location: '',
      bio: '',
      experience_years: 0,
      skills: [],
    },
  });
  const [passwordData, setPasswordData] = useState<PasswordFormData>({
    old_password: '',
    new_password: '',
    new_password_confirm: '',
  });
  const [profileErrors, setProfileErrors] = useState<FormErrors>({});
  const [passwordErrors, setPasswordErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [skillInput, setSkillInput] = useState<string>('');

  // Initialize form data with user data
  useEffect(() => {
    if (state.user) {
      setProfileData({
        first_name: state.user.first_name || '',
        last_name: state.user.last_name || '',
        profile: {
          phone: state.user.profile?.phone || '',
          location: state.user.profile?.location || '',
          bio: state.user.profile?.bio || '',
          experience_years: state.user.profile?.experience_years || 0,
          skills: state.user.profile?.skills || [],
        },
      });
    }
  }, [state.user]);

  const validateProfileForm = (): boolean => {
    const errors: FormErrors = {};

    if (!profileData.first_name.trim()) {
      errors.first_name = 'First name is required';
    }

    if (!profileData.last_name.trim()) {
      errors.last_name = 'Last name is required';
    }

    if (profileData.profile.phone && !/^\+?[\d\s\-\(\)]+$/.test(profileData.profile.phone)) {
      errors.phone = 'Please enter a valid phone number';
    }

    if (profileData.profile.experience_years < 0 || profileData.profile.experience_years > 50) {
      errors.experience_years = 'Experience years must be between 0 and 50';
    }

    setProfileErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const validatePasswordForm = (): boolean => {
    const errors: FormErrors = {};

    if (!passwordData.old_password) {
      errors.old_password = 'Current password is required';
    }

    if (!passwordData.new_password) {
      errors.new_password = 'New password is required';
    } else if (passwordData.new_password.length < 8) {
      errors.new_password = 'Password must be at least 8 characters';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(passwordData.new_password)) {
      errors.new_password = 'Password must contain uppercase, lowercase, and number';
    }

    if (!passwordData.new_password_confirm) {
      errors.new_password_confirm = 'Please confirm your new password';
    } else if (passwordData.new_password !== passwordData.new_password_confirm) {
      errors.new_password_confirm = 'Passwords do not match';
    }

    setPasswordErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleProfileInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    
    if (name.startsWith('profile.')) {
      const profileField = name.replace('profile.', '');
      setProfileData(prev => ({
        ...prev,
        profile: {
          ...prev.profile,
          [profileField]: profileField === 'experience_years' ? parseInt(value) || 0 : value,
        },
      }));
    } else {
      setProfileData(prev => ({ ...prev, [name]: value }));
    }

    // Clear field error
    if (profileErrors[name]) {
      setProfileErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handlePasswordInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({ ...prev, [name]: value }));

    // Clear field error
    if (passwordErrors[name]) {
      setPasswordErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleAddSkill = () => {
    if (skillInput.trim() && !profileData.profile.skills.includes(skillInput.trim())) {
      setProfileData(prev => ({
        ...prev,
        profile: {
          ...prev.profile,
          skills: [...prev.profile.skills, skillInput.trim()],
        },
      }));
      setSkillInput('');
    }
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    setProfileData(prev => ({
      ...prev,
      profile: {
        ...prev.profile,
        skills: prev.profile.skills.filter(skill => skill !== skillToRemove),
      },
    }));
  };

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateProfileForm()) {
      return;
    }

    setIsSubmitting(true);
    setLoading(true);
    setError(null);
    setSuccessMessage('');

    try {
      const updateData: UpdateProfileRequest = {
        first_name: profileData.first_name,
        last_name: profileData.last_name,
        profile: profileData.profile,
      };

      const response = await authService.updateProfile(updateData);
      updateUser(response.data);
      setSuccessMessage('Profile updated successfully!');
    } catch (error: any) {
      console.error('Profile update error:', error);
      
      if (error.details) {
        setProfileErrors(error.details);
      } else {
        setError(error.message || 'Failed to update profile');
      }
    } finally {
      setIsSubmitting(false);
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validatePasswordForm()) {
      return;
    }

    setIsSubmitting(true);
    setLoading(true);
    setError(null);
    setSuccessMessage('');

    try {
      const changeData: ChangePasswordRequest = {
        old_password: passwordData.old_password,
        new_password: passwordData.new_password,
        new_password_confirm: passwordData.new_password_confirm,
      };

      await authService.changePassword(changeData);
      setSuccessMessage('Password changed successfully!');
      setPasswordData({
        old_password: '',
        new_password: '',
        new_password_confirm: '',
      });
    } catch (error: any) {
      console.error('Password change error:', error);
      
      if (error.details) {
        setPasswordErrors(error.details);
      } else {
        setError(error.message || 'Failed to change password');
      }
    } finally {
      setIsSubmitting(false);
      setLoading(false);
    }
  };

  if (!state.user) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">Please log in to view your profile.</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white shadow-md rounded-lg">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Profile tabs">
            <button
              onClick={() => setActiveTab('profile')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'profile'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              aria-current={activeTab === 'profile' ? 'page' : undefined}
            >
              Profile Information
            </button>
            <button
              onClick={() => setActiveTab('password')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'password'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              aria-current={activeTab === 'password' ? 'page' : undefined}
            >
              Change Password
            </button>
          </nav>
        </div>

        <div className="p-6">
          {successMessage && (
            <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded" role="alert">
              {successMessage}
            </div>
          )}

          {activeTab === 'profile' && (
            <form onSubmit={handleProfileSubmit}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-2">
                    First Name
                  </label>
                  <input
                    type="text"
                    id="first_name"
                    name="first_name"
                    value={profileData.first_name}
                    onChange={handleProfileInputChange}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      profileErrors.first_name ? 'border-red-500' : 'border-gray-300'
                    }`}
                    aria-invalid={!!profileErrors.first_name}
                    required
                  />
                  {profileErrors.first_name && (
                    <p className="text-red-500 text-xs mt-1" role="alert">
                      {profileErrors.first_name}
                    </p>
                  )}
                </div>

                <div>
                  <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-2">
                    Last Name
                  </label>
                  <input
                    type="text"
                    id="last_name"
                    name="last_name"
                    value={profileData.last_name}
                    onChange={handleProfileInputChange}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      profileErrors.last_name ? 'border-red-500' : 'border-gray-300'
                    }`}
                    aria-invalid={!!profileErrors.last_name}
                    required
                  />
                  {profileErrors.last_name && (
                    <p className="text-red-500 text-xs mt-1" role="alert">
                      {profileErrors.last_name}
                    </p>
                  )}
                </div>

                <div>
                  <label htmlFor="profile.phone" className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    id="profile.phone"
                    name="profile.phone"
                    value={profileData.profile.phone}
                    onChange={handleProfileInputChange}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      profileErrors.phone ? 'border-red-500' : 'border-gray-300'
                    }`}
                    aria-invalid={!!profileErrors.phone}
                  />
                  {profileErrors.phone && (
                    <p className="text-red-500 text-xs mt-1" role="alert">
                      {profileErrors.phone}
                    </p>
                  )}
                </div>

                <div>
                  <label htmlFor="profile.location" className="block text-sm font-medium text-gray-700 mb-2">
                    Location
                  </label>
                  <input
                    type="text"
                    id="profile.location"
                    name="profile.location"
                    value={profileData.profile.location}
                    onChange={handleProfileInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="City, State/Country"
                  />
                </div>

                <div>
                  <label htmlFor="profile.experience_years" className="block text-sm font-medium text-gray-700 mb-2">
                    Years of Experience
                  </label>
                  <input
                    type="number"
                    id="profile.experience_years"
                    name="profile.experience_years"
                    value={profileData.profile.experience_years}
                    onChange={handleProfileInputChange}
                    min="0"
                    max="50"
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      profileErrors.experience_years ? 'border-red-500' : 'border-gray-300'
                    }`}
                    aria-invalid={!!profileErrors.experience_years}
                  />
                  {profileErrors.experience_years && (
                    <p className="text-red-500 text-xs mt-1" role="alert">
                      {profileErrors.experience_years}
                    </p>
                  )}
                </div>
              </div>

              <div className="mt-6">
                <label htmlFor="profile.bio" className="block text-sm font-medium text-gray-700 mb-2">
                  Bio
                </label>
                <textarea
                  id="profile.bio"
                  name="profile.bio"
                  value={profileData.profile.bio}
                  onChange={handleProfileInputChange}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Tell us about yourself..."
                />
              </div>

              <div className="mt-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Skills
                </label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={skillInput}
                    onChange={(e) => setSkillInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddSkill())}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Add a skill..."
                  />
                  <button
                    type="button"
                    onClick={handleAddSkill}
                    className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {profileData.profile.skills.map((skill, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                    >
                      {skill}
                      <button
                        type="button"
                        onClick={() => handleRemoveSkill(skill)}
                        className="ml-2 text-blue-600 hover:text-blue-800 focus:outline-none"
                        aria-label={`Remove ${skill} skill`}
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              <div className="mt-8">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className={`px-6 py-2 rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    isSubmitting
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-blue-500 hover:bg-blue-600 text-white'
                  }`}
                >
                  {isSubmitting ? 'Updating...' : 'Update Profile'}
                </button>
              </div>
            </form>
          )}

          {activeTab === 'password' && (
            <form onSubmit={handlePasswordSubmit}>
              <div className="max-w-md">
                <div className="mb-4">
                  <label htmlFor="old_password" className="block text-sm font-medium text-gray-700 mb-2">
                    Current Password
                  </label>
                  <input
                    type="password"
                    id="old_password"
                    name="old_password"
                    value={passwordData.old_password}
                    onChange={handlePasswordInputChange}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      passwordErrors.old_password ? 'border-red-500' : 'border-gray-300'
                    }`}
                    aria-invalid={!!passwordErrors.old_password}
                    autoComplete="current-password"
                    required
                  />
                  {passwordErrors.old_password && (
                    <p className="text-red-500 text-xs mt-1" role="alert">
                      {passwordErrors.old_password}
                    </p>
                  )}
                </div>

                <div className="mb-4">
                  <label htmlFor="new_password" className="block text-sm font-medium text-gray-700 mb-2">
                    New Password
                  </label>
                  <input
                    type="password"
                    id="new_password"
                    name="new_password"
                    value={passwordData.new_password}
                    onChange={handlePasswordInputChange}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      passwordErrors.new_password ? 'border-red-500' : 'border-gray-300'
                    }`}
                    aria-invalid={!!passwordErrors.new_password}
                    autoComplete="new-password"
                    required
                  />
                  {passwordErrors.new_password && (
                    <p className="text-red-500 text-xs mt-1" role="alert">
                      {passwordErrors.new_password}
                    </p>
                  )}
                </div>

                <div className="mb-6">
                  <label htmlFor="new_password_confirm" className="block text-sm font-medium text-gray-700 mb-2">
                    Confirm New Password
                  </label>
                  <input
                    type="password"
                    id="new_password_confirm"
                    name="new_password_confirm"
                    value={passwordData.new_password_confirm}
                    onChange={handlePasswordInputChange}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      passwordErrors.new_password_confirm ? 'border-red-500' : 'border-gray-300'
                    }`}
                    aria-invalid={!!passwordErrors.new_password_confirm}
                    autoComplete="new-password"
                    required
                  />
                  {passwordErrors.new_password_confirm && (
                    <p className="text-red-500 text-xs mt-1" role="alert">
                      {passwordErrors.new_password_confirm}
                    </p>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className={`px-6 py-2 rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    isSubmitting
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-blue-500 hover:bg-blue-600 text-white'
                  }`}
                >
                  {isSubmitting ? 'Changing Password...' : 'Change Password'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};