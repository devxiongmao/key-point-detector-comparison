require 'mechanize'
require 'fileutils'
require 'pry'
require 'rb-readline'
class TestAgent

  def initialize
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    @matching_image_1 = {0 => 'bark1.png', 1 => 'box.png', 2 => 'rushmore2.png'}
    @matching_image_2 = {0 => 'bark2.png', 1 => 'box_in_scene.png', 2 => 'rushmore1.png'}
    @stitching_image_1 = {0 => 'left.jpg', 1 => 'Panorama_1.jpg', 2 => 'panorama_image1.jpg'}
    @stitching_image_2 = {0 => 'right.jpg', 1 => 'Panorama_2.jpg', 2 => 'panorama_image2.jpg'}

    @agent = Mechanize.new do |a|
      a.user_agent = user_agent
    end
    @agent.agent.http.verify_mode = OpenSSL::SSL::VERIFY_NONE
  end

  def prep_folders(n, name)
    n.times do |i|
      FileUtils.mkdir_p "#{name}/#{i}"
    end

  end

  def subsequent_request_test(n, url)
    n.times do |i|
      begin
        main_page = @agent.get(url)
        form = main_page.forms[0]

        type = rand(2)

        if type == 0

          detector = rand(5) # Since we have 5 detectors

          case detector
          when 0
            form.checkbox_with(:value => 'SURF-Detector').check
            detector_used = "SURF"
          when 1
            form.checkbox_with(:value => 'SIFT-Detector').check
            detector_used = "SURF"
          when 2
            detector_used = "FAST"
            form.checkbox_with(:value => 'FAST-Detector').check
          when 3
            detector_used = "ORB"
            form.checkbox_with(:value => 'ORB-Detector').check
          when 4
            detector_used = "Harris"
            form.checkbox_with(:value => 'Harris-Detector').check
          end

          form.checkbox_with(:value => 'SIFT-Descriptor').check
          form['num-keypoints'] = "1000"
          form.radiobutton_with(:value => 'default').check
          # Do Matching
          puts "Matching"
          form.radiobutton_with(:value => 'matching').check
          image_num = rand(3) # since we have 3 sets
          image_name_1 = @matching_image_1[image_num]
          image_name_2 = @matching_image_2[image_num]

          form.file_uploads[0].file_name = "matching_images/#{image_name_1}"
          form.file_uploads[1].file_name = "matching_images/#{image_name_2}"
          page_final = form.submit
          open("ConsecutiveRequests/#{i}/params.txt", 'w') { |f| f.puts "MATCHING: #{image_name_1}/#{image_name_2} with #{detector_used}" }
          download_link = page_final.css("a").map { |link| link['href'] }
          @agent.pluggable_parser.default = Mechanize::Download
          @agent.get(download_link[0]).save("ConsecutiveRequests/#{i}/result.png")

        else
          # Do stitching
          detector = rand(3) # Since we have 5 detectors
          form['num-keypoints'] = "1000"

          case detector
          when 0
            form.checkbox_with(:value => 'SURF-Detector').check
            detector_used = "SURF"
          when 1
            form.checkbox_with(:value => 'SIFT-Detector').check
            detector_used = "SURF"
          when 2
            detector_used = "ORB"
            form.checkbox_with(:value => 'ORB-Detector').check
          end

          form.checkbox_with(:value => 'SIFT-Descriptor').check

          form.radiobutton_with(:value => 'default').check
          puts "Stitching"
          form.radiobutton_with(:value => 'stitching').check
          image_num = rand(3) # since we have 3 sets
          image_name_1 = @stitching_image_1[image_num]
          image_name_2 = @stitching_image_2[image_num]


          form.file_uploads[0].file_name = "stitching/#{image_name_1}"
          form.file_uploads[1].file_name = "stitching/#{image_name_2}"
          page_final = form.submit
          open("ConsecutiveRequests/#{i}/params.txt", 'w') { |f| f.puts "STITCHING: #{image_name_1}/#{image_name_2} with #{detector_used}" }

          download_link = page_final.css("a").map { |link| link['href'] }
          @agent.pluggable_parser.default = Mechanize::Download

          @agent.get(download_link[0]).save("ConsecutiveRequests/#{i}/result.png")

        end

      rescue StandardError => error
        raise "Crash at #{i} requests"
      end
    end
  end

  def test_concurrent_users(n, url)
    threads = []
    n.times do |i|
      threads << Thread.new do     
        begin
          main_page = @agent.get(url)
          form = main_page.forms[0]


          type = rand(2)

          if type == 0
            detector = rand(5) # Since we have 5 detectors

            case detector
            when 0
              form.checkbox_with(:value => 'SURF-Detector').check
              detector_used = "SURF"
            when 1
              form.checkbox_with(:value => 'SIFT-Detector').check
              detector_used = "SURF"
            when 2
              detector_used = "FAST"
              form.checkbox_with(:value => 'FAST-Detector').check
            when 3
              detector_used = "ORB"
              form.checkbox_with(:value => 'ORB-Detector').check
            when 4
              detector_used = "Harris"
              form.checkbox_with(:value => 'Harris-Detector').check
            end

            form.checkbox_with(:value => 'SIFT-Descriptor').check

            form.radiobutton_with(:value => 'default').check


            # Do Matching
            puts "Matching"
            form.radiobutton_with(:value => 'matching').check
            image_num = rand(3) # since we have 3 sets
            image_name_1 = @matching_image_1[image_num]
            image_name_2 = @matching_image_2[image_num]

            form.file_uploads[0].file_name = "matching_images/#{image_name_1}"
            form.file_uploads[1].file_name = "matching_images/#{image_name_2}"
            page_final = form.submit
            open("ConcurrentRequests/#{i}/params.txt", 'w') { |f| f.puts "MATCHING: #{image_name_1}/#{image_name_2} with #{detector_used}" }
            download_link = page_final.css("a").map { |link| link['href'] }
            @agent.pluggable_parser.default = Mechanize::Download
            @agent.get(download_link[0]).save("ConcurrentRequests/#{i}/result.png")

          else
            detector = rand(3) # Since we have 3 detectors

            case detector
            when 0
              form.checkbox_with(:value => 'SURF-Detector').check
              detector_used = "SURF"
            when 1
              form.checkbox_with(:value => 'SIFT-Detector').check
              detector_used = "SIFT"
            when 2
              detector_used = "ORB"
              form.checkbox_with(:value => 'ORB-Detector').check
            end

            form.checkbox_with(:value => 'SIFT-Descriptor').check

            form.radiobutton_with(:value => 'default').check


            # Do stitching
            puts "Stitching"
            form.radiobutton_with(:value => 'stitching').check
            image_num = rand(3) # since we have 3 sets
            image_name_1 = @stitching_image_1[image_num]
            image_name_2 = @stitching_image_2[image_num]


            form.file_uploads[0].file_name = "stitching/#{image_name_1}"
            form.file_uploads[1].file_name = "stitching/#{image_name_2}"
            page_final = form.submit
            open("ConcurrentRequests/#{i}/params.txt", 'w') { |f| f.puts "STITCHING: #{image_name_1}/#{image_name_2} with #{detector_used}" }

            download_link = page_final.css("a").map { |link| link['href'] }
            @agent.pluggable_parser.default = Mechanize::Download

            @agent.get(download_link[0]).save("ConcurrentRequests/#{i}/result.png")

          end
        rescue StandardError => error
          raise "Crash at #{i} requests"
        end
      end
    end
    threads.map(&:join)
  end
end

number_of_requests = 1000
link = 'http://localhost:5000'
agent = TestAgent.new
agent.prep_folders(number_of_requests, "ConsecutiveRequests")
agent.subsequent_request_test(number_of_requests, link)
puts "Subequent Request Test Passed!"
number_of_requests = 500
agent.prep_folders(number_of_requests, "ConcurrentRequests")
agent.test_concurrent_users(number_of_requests, link)
puts "Concurrent Request Test Passed!"
